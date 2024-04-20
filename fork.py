from typing import List
import uvicorn, multiprocessing, secrets, json
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect,Depends,Request
from uuid import uuid4
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from starlette.middleware.sessions import SessionMiddleware
import os
import asyncio
import time

app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"
semaphore = asyncio.Semaphore(20)
request_count = 0
log_lock=multiprocessing.Lock()

app.add_middleware(SessionMiddleware, secret_key = SECRET_KEY)

class ConnectionManager:

	def __init__(self):
		self.active_connections: List[WebSocket] = []


	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.active_connections.append(websocket)


	async def disconnect(self, websocket: WebSocket):
		self.active_connections.remove(websocket)


	async def send_personal_message(self, message: str, websocket: WebSocket):
		await websocket.send_text(message)


	async def broadcast(self, message: str, websocket: WebSocket):
		for connection in self.active_connections:
			if(connection!=websocket):
				await connection.send_text(message)
			

connectionmanager = ConnectionManager()


def generate_session_id():
    return secrets.token_hex(16)  

@app.get("/")
async def home(request: Request):
	print(multiprocessing.get_start_method())	
	server_port = os.environ.get("PORT")
	return templates.TemplateResponse("index.html", {"request" : request, "port": server_port})

async def handle_client(websocket:WebSocket):
	while True:	
			
			data = websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
			await connectionmanager.broadcast(f"Client#: {data}", websocket)
	

@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int,server_id:str):	
	
	try:
		await connectionmanager.connect(websocket)
		pid = os.fork()
		if(pid == 0):
			await handle_client(websocket)
			os._exit(0)
		else:			
			return
		
	except WebSocketDisconnect:
		
		connectionmanager.disconnect(websocket)

		
def run_server(port):
	os.environ["PORT"]=str(port)
	uvicorn.run("fork:app", host="127.0.0.1", port = port)

if __name__ == "__main__":
	processes=[]
	ports=[8001,8002,8003]
	for port in ports:
		process = multiprocessing.Process(target = run_server,args = (port,))
		process.start()
		processes.append(process)

	for process in processes:
		process.join()









# https://www.geeksforgeeks.org/understanding-fork-and-spawn-in-python-multiprocessing/