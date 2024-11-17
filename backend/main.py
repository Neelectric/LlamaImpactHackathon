# 
# System imports
import json
from os import getenv, path
import os
import subprocess
import random  # for demo data generation
from typing import Dict, Set
import asyncio
import base64

# External imports
# from dotenv import load_dotenv
from pydantic import BaseModel
import ollama
from openai import OpenAI
from groq import Groq

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

# Local imports
from read_data import DataQuery



# Read in environment variables
app_base_path = path.dirname(__file__)
app_root_path = path.join(app_base_path, '..//')
# load_dotenv(dotenv_path=path.join(app_root_path, '.env'))

server_http_host='127.0.0.1'
api_http_port=5001
api_http_url='http://127.0.0.1:5001'

ui_folder_root='frontend'
ui_proxy_launch_cmd = 'npm run dev'

app_frontend_path = path.join(app_root_path, ui_folder_root)



# Launch the app
class Question(BaseModel):
    prompt: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, str] = {}  # WebSocket: active_option

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = None

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def set_client_option(self, websocket: WebSocket, option: str):
        self.active_connections[websocket] = option

    def get_client_option(self, websocket: WebSocket) -> str:
        return self.active_connections.get(websocket)


app = FastAPI()
manager = ConnectionManager()

# # ----------------------VLLM DEFS START
# openai_api_key = "EMPTY"
# openai_api_base = "http://localhost:30000/v1"
# client = OpenAI(
#     # defaults to os.environ.get("OPENAI_API_KEY")
#     api_key=openai_api_key,
#     base_url=openai_api_base,
# )
# models = client.models.list()
# model = models.data[0].id
# def ask_vllm(prompt, image_path):
#     chat_completion_from_url = client.chat.completions.create(
#         messages=[{
#             "role":
#             "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": prompt,
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "file://backend/" + image_path
#                     },
#                 },
#             ],
#         }],
#         model=model,
#         max_completion_tokens=600,
#         temperature=0.5,
#     )
#     result = chat_completion_from_url.choices[0].message.content
    # return result
# -----------------------VLLM DEFS FINISH



# ----------------------GROQ DEFS START
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
with open('../env.txt', 'r') as file:
    lines = file.readlines()
client = Groq(api_key=lines[0].strip())

def ask_groq(prompt, image_path):
    base64_image = encode_image(image_path)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", 
                     "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,

        )
    message = chat_completion.choices[0].message
    content = message.content
    return content
# ----------------------GROQ DEFS FINISH


def ask_ollama(prompt, image_path):
    response = ollama.chat(
        model='llama3.2-vision',
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_path]
        }],
        options={
        "temperature": 0.5
        },
    )
    response_text = response["message"]["content"]
    return response_text



# @app.post('/ask')
async def ask(tweet_content, image_path):
    # prompt = "You are being provided with the content and attached image of a tweet. You are a part of a system that monitors tweets worldwide to detect a sudden spike in tweets relating to natural disasters. To this end, you are required to output a 'Natural Disaster Score'. This score goes from 0 to 10, where 0 refers to 'No apparent indicators of a natural disaster currently taking place', and 10 refers to 'Natural disaster clearly imminent or underway, requiring immediate attention and threatening or having already caused severe loss of life'. Consequently, your role is extremely important and has the potential to save human lives. It is crucial for you to be incredibly attentive and pay close attention to specific details in the images or tweet contents which may indicate any information relating to natural disasters. At the same time, make sure you consider the risks of false resource allocation stemming from false positives."
    prompt = f"""Using the provided image and the accompanying tweet {tweet_content}, output a 'Natural Disaster Score'. This score goes from 0 to 10, where:
                - 0 refers to 'No apparent indicators of a natural disaster currently taking place'
                - 5 refers to 'Some indicators of a potential natural disaster may be present, though full clarity is not yet available so further investigation is necessary'
                - 10 refers to 'Natural disaster clearly imminent or underway, requiring immediate attention and threatening or having already caused severe loss of life'.
                Do not hallucinate. Consider the risk of false negatives, and return a judgmenet of 0 if no indicators of disasters are present.
                Please output your judgement in json format, with the following fields:
                {{
                "chain_of_thought": "",
                "final_judgement_out_of_10": ,
                }}
                The following are examples for you to follow:
                {{
                "chain_of_thought": "The image shows a man in a black shirt and hat, with a serious expression. The text on his shirt reads 'FAMILY' and 'LIF'. The image also shows a brick wall in the background. There is no clear indication of a natural disaster in the image.",
                "final_judgement_out_of_10": 0
                }}
                {{
                "chain_of_thought": "A torrential downpour appears to be taking place in the area, possibly triggering a flood. However, an ambulance has also been spotted near the scene of destruction, which may indicate that the impact is localised, threatening life. A more intense review suggests that the scale of the devastation is too vast for any timely rescue operations, confirming that a disastrous flood has indeed occurred.",
                "final_judgement_out_of_10": 7
                }}
                 """
    response = ask_groq(prompt, image_path)
    return response

async def generate_option_data(option: str, dq: DataQuery) -> str:
    if option == "tweet_feed":
        tweet_id, tweet_content, image_path = dq.get_next()
        image_path = image_path[0]
        llama_response = await ask(tweet_content=tweet_content, image_path=image_path)
        try:
            result_dict = json.loads(llama_response)
            print(result_dict)
            result_dict["type"] = "tweet"
            result_dict["id"] = str(tweet_id),
            result_dict["content"] = tweet_content,
            result_dict["image_path"] = image_path[0],
            result_dict["final_judgement_out_of_10"] = int(result_dict["final_judgement_out_of_10"])

        except Exception as error:
            print(error)
            result_dict = {
                "type": "tweet",
                "id": str(tweet_id),
                "content": tweet_content,
                "image_path": image_path[0],
                "chain_of_thought": llama_response,
                "final_judgement_out_of_10": 0,
                "timestamp": "2024-03-16T10:00:00Z",  # You might want to get this from the tweet data
            }
        print(result_dict["final_judgement_out_of_10"])

        # print(result_dict)
        return json.dumps(result_dict)
    # Keep your existing options...
    return json.dumps({"error": "Invalid option"})


# Modify the websocket_endpoint function to pass the DataQuery instance:
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("starting websocket endpoint")
    dq = DataQuery("california_wildfires_final_data_tweets.json")  # Create instance here or pass it as parameter
    await manager.connect(websocket)
    print("manager connected websocket!")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if "option" in message:
                    manager.set_client_option(websocket, message["option"])
                    await websocket.send_text(json.dumps({"status": "option_set", "option": message["option"]}))
                    
                    while True:
                        current_option = manager.get_client_option(websocket)
                        if current_option:
                            data = await generate_option_data(current_option, dq)
                            await websocket.send_text(data)
                        await asyncio.sleep(5)  # Send tweet every second
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Route for testing the API
@app.get("/")
async def root():

    # response_text = response["message"]["content"]
    print("OVERWRITING RESPONSE TEXT")
    response_text = "temp"
    print(response_text)
    return {"message": "Hello from FastAPI!"}




if __name__ == "__main__":
    # Launch the frontend app as a separate Python subprocess
    # (essentially just goes to the frontend server and runs 'npm run dev' there for us)

    # spa_process = subprocess.Popen(
    #     args=ui_proxy_launch_cmd.split(" "),
    #     cwd='C:/Users/jonai/Code/LlamaImpactHackathon/frontend',
    #     shell=True
    # )

    # Launch the backend server
    # Uvicorn is a server programme that runs the 'app' object in 'main.py' (here)
    print("about to launch uvicorn")
    # dq = DataQuery("california_wildfires_final_data_tweets.json")
    # print(dq.get_next())
    uvicorn.run(
        "main:app", 
        host=server_http_host, 
        port=5001,
        reload=True
        )
    print("killing uvicorn")