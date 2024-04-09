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
semaphore = asyncio.Semaphore(20)
app.add_middleware(SessionMiddleware, secret_key = SECRET_KEY)
# contains the broadcasting code ..

class ConnectionManager:

	def __init__(self):
		self.active_connections: List[WebSocket] = []
		self.server_ws:WebSocket


	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.active_connections.append(websocket)


	def disconnect(self, websocket: WebSocket):
		self.active_connections.remove(websocket)


	async def send_personal_message(self, message: str, websocket: WebSocket):
		await websocket.send_text(message)
	
	async def send_to_master(self,message:str):
		await self.server_ws.send_text(message)


	async def broadcast(self, message: str, websocket: WebSocket):
		tasks = [connection.send_text(message) for connection in self.active_connections if connection != websocket]
		await asyncio.gather(*tasks)	
	
	async def broadcast_other(self, message: str):
		tasks = [connection.send_text(message) for connection in self.active_connections]
		await asyncio.gather(*tasks)
		
	async def master_connect(self,websocket:WebSocket):
		await websocket.accept()
		self.server_ws = websocket

			

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
	# print(a)
	server_port = os.environ.get("PORT")
	# print("hi",server_port)
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	
	return templates.TemplateResponse("index_copy.html", {"request" : request, "port": server_port})


@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int):
	
	try:
		await try_connection(websocket)
		while True:

			data = await websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
			await connectionmanager.broadcast(f"Client {client_id}#: {data}", websocket)

	except WebSocketDisconnect:
		connectionmanager.disconnect(websocket)

	finally:
		semaphore.release()

@app.websocket("/ws1")
async def websocket_endpt(websocket:WebSocket):
	try:
		await connectionmanager.master_connect(websocket)

		while True:

			msg = await websocket.receive_text()
			await connectionmanager.broadcast_other(f"client:{msg}")

	except WebSocketDisconnect:
		# connectionmanager.disconnect(websocket)
		print("disconnected")



def run_server(port):
	os.environ["PORT"]=str(port)
	# ws = websockets.connect("ws://localhost:6000/ws")
	uvicorn.run("app:app", host="127.0.0.1", port = port)

if __name__ == "__main__":
		processes=[]
		ports=[8001,8002,8003]
		for port in ports:
			process = multiprocessing.Process(target = run_server,args = (port,))
			process.start()
			processes.append(process)

		for process in processes:
			process.join()








# ws = websockets.connect("ws://localhost:8000/ws")
	# print(ws)
	# ws_json=json.dumps({'url':ws.url, 'headers':ws.headers})
	# os.environ["WS"]=ws_json
# print("hello"+session.get("session_id"))
	# port = request.query_params.get('var', '')
	# dict={'port':port}
	# semaphore-=1
			


# ws_json = os.getenv("WS")
# ws_data=json.loads(ws_json)
# ws_restore=websockets.connect(ws_data['url'],header=ws_data['headers'])
# print(ws_restore)
