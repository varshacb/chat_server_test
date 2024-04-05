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
import websockets
# from dotenv import load_dotenv
import time
app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"
semaphore = asyncio.Semaphore(2)
app.add_middleware(SessionMiddleware, secret_key = SECRET_KEY)


class ConnectionManager:

	def __init__(self):
		self.active_connections: List[WebSocket] = []


	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.active_connections.append(websocket)


	def disconnect(self, websocket: WebSocket):
		self.active_connections.remove(websocket)


	async def send_personal_message(self, message: str, websocket: WebSocket):
		await websocket.send_text(message)


	async def broadcast(self, message: str, websocket: WebSocket):
		# tasks = [connection.send_text(message) for connection in self.active_connections if connection != websocket]
		# await asyncio.gather(*tasks)	
		# print(message )
		for connection in self.active_connections:
			if connection != websocket:
				connection.send_text(message)
			

connectionmanager = ConnectionManager()


def generate_session_id():
    return secrets.token_hex(16)  

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "X-Backend-Port"
    return response

async def try_connection(websocket: WebSocket):
	global semaphore
	if await semaphore.acquire():
		try:
			await connectionmanager.connect(websocket)
			return  
		except:
			semaphore.release() 
			raise
   
@app.get("/")
async def home(request: Request):
	server_port = os.environ.get("PORT")
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	
	return templates.TemplateResponse("index1.html", {"request" : request,"port":server_port})


async def handle_client(websocket: WebSocket):
	try:
		while True:

			data = await websocket.receive_text() 
			connectionmanager.send_personal_message(f"You : {data}", websocket) 
			connectionmanager.broadcast(f"Client#: {data}", websocket)

	except WebSocketDisconnect:
		connectionmanager.disconnect(websocket)

@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int):
	await websocket.accept()
	
	pid = os.fork()
	if pid == 0:  
		await handle_client(websocket)
		os._exit(0)  
	else: 
		return 
    
def run_server(port):
	os.environ["PORT"]=str(port)
	uvicorn.run(app, host="127.0.0.1", port = port)
	

if __name__ == "__main__":
		processes=[]
		ports=[8001,8002,8003]
		for port in ports:
			process = multiprocessing.Process(target = run_server,args = (port,))
			process.start()
			processes.append(process)

		for process in processes:
			process.join()
	


