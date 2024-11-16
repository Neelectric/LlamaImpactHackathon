# Main driver file to prompt our model
# System imports
import json
from os import getenv, path
import subprocess

# External imports
from dotenv import load_dotenv
from pydantic import BaseModel
import ollama

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import uvicorn

# Local imports



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

app = FastAPI()
in_game = False


# Define global variables
# @app.on_event("startup")
# def startup_event():
#     global llm
#     llm = LLM(device)

# Route for testing the API
@app.get("/")
async def root():
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
            'content': 'What is in this image?',
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
    uvicorn.run("main:app", host=server_http_host, port=api_http_port)