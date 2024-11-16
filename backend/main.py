# 
# System imports
import json
from os import getenv, path
import subprocess
import random  # for demo data generation
from typing import Dict, Set
import asyncio

# External imports
from dotenv import load_dotenv
from pydantic import BaseModel
import ollama

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

# Local imports
from read_data import DataQuery



# Read in environment variables
app_base_path = path.dirname(__file__)
app_root_path = path.join(app_base_path, '../')
load_dotenv(dotenv_path=path.join(app_root_path, '.env'))

server_http_host=getenv("SERVER_HTTP_HOST")
api_http_port=int(getenv("API_HTTP_PORT"))
api_http_url=getenv("API_HTTP_URL")

ui_folder_root="frontend"
ui_proxy_launch_cmd = getenv("UI_PROXY_LAUNCH_CMD")

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
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002", "http://127.0.0.1:3002"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
manager = ConnectionManager()

async def generate_option_data(option: str, dq: DataQuery) -> str:
    if option == "tweet_feed":
        tweet_id, tweet_content, image_path = dq.get_next()
        return json.dumps({
            "type": "tweet",
            "id": tweet_id,
            "content": tweet_content,
            "image_path": image_path,
            "timestamp": "2024-03-16T10:00:00Z"  # You might want to get this from the tweet data
        })
    # Keep your existing options...
    return json.dumps({"error": "Invalid option"})


# Modify the websocket_endpoint function to pass the DataQuery instance:
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    dq = DataQuery("california_wildfires_final_data.json")  # Create instance here or pass it as parameter
    await manager.connect(websocket)
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
                        await asyncio.sleep(1)  # Send tweet every second
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)




# @app.on_event("startup")
# async def on_startup():
#     # Call the root function
#     response = await root()
#     print("Startup Response:", response)

# Route for testing the API
@app.get("/")
async def root():
    # response = ollama.chat(
    #     model='llama3.2-vision',
    #     messages=[{
    #         'role': 'user',
    #         'content': 'What is in this image?',
    #         'images': ['water_helpers.jpg']
    #     }],
    #     options={
    #     "temperature": 0
    #     },
    # )

    # response_text = response["message"]["content"]
    print("OVERWRITING RESPONSE TEXT")
    response_text = "temp"
    print(response_text)
    return {"message": "Hello from FastAPI!"}

# Route for getting a response to a query
@app.post('/ask')
async def ask(question: Question):
    # print(question)
    prompt = question.prompt
    response = ollama.chat(
        model='llama3.2-vision',
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': ['water_helpers.jpg']
        }],
        options={
        "temperature": 0
        },
    )

    response_text = response["message"]["content"]

    return StreamingResponse(
        response_text,
        media_type='text/event-stream'
    )



if __name__ == "__main__":
    # Launch the frontend app as a separate Python subprocess
    # (essentially just goes to the frontend server and runs 'npm run dev' there for us)
    spa_process = subprocess.Popen(
        args=ui_proxy_launch_cmd.split(" "),
        cwd=app_frontend_path
    )

    # Launch the backend server
    # Uvicorn is a server programme that runs the 'app' object in 'main.py' (here)
    print("about to launch uvicorn")
    dq = DataQuery("california_wildfires_final_data.json")
    print(dq.get_next())
    uvicorn.run(
        "main:app", 
        host=server_http_host, 
        port=api_http_port,
        reload=True
        )
    print("launched uvicorn")