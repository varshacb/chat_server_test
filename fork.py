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
from multiprocessing import Semaphore
# from dotenv import load_dotenv
import time

app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"
semaphore = Semaphore(1)
app.add_middleware(SessionMiddleware, secret_key = SECRET_KEY)


class ConnectionManager:

	def __init__(self):
		self.active_connections: List[WebSocket] = []


	def connect(self, websocket: WebSocket):
		websocket.accept()
		self.active_connections.append(websocket)


	def disconnect(self, websocket: WebSocket):
		self.active_connections.remove(websocket)


	async def send_personal_message(self, message: str, websocket: WebSocket):
		await websocket.send_text(message)


	async def broadcast(self, message: str, websocket: WebSocket):
		tasks = [connection.send_text(message) for connection in self.active_connections if connection != websocket]
		await asyncio.gather(*tasks)	
			

connectionmanager = ConnectionManager()


def generate_session_id():
    return secrets.token_hex(16)  

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "X-Backend-Port"
    return response

def try_connection(websocket: WebSocket):
	global semaphore
	print("inside try_con")
	if semaphore.acquire():
		try:
			print("inside try ...")
			connectionmanager.connect(websocket)
			return  
		except:
			semaphore.release() 
			raise
		
limit=1
def conn(websocket:WebSocket):
	if(limit>0):
		connectionmanager.connect(websocket)
		limit-=1
	else:
		print("server busy")
	


@app.get("/")
async def home(request: Request):
	server_port = os.environ.get("PORT")
	# print("hi",server_port)
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	
	return templates.TemplateResponse("index_copy.html", {"request" : request, "port": server_port})

def handle_client(websocket: WebSocket):
	while True:
		data = websocket.receive_text() 
		if not data:
			break
		websocket.send(data)
		
	websocket.close()


@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int):
	try:
		# conn(websocket)
		while True:
			websocket.accept()
			print("indide while")
			pid = os.fork()
			print("after fork")
			if pid == 0:
				print("inside child")
				handle_client(websocket)
				os._exit(0)
			else:
				return
	except WebSocketDisconnect:
		connectionmanager.disconnect(websocket)

	# finally:
	# 	limit+=1
		
	# print("inside ws endpoint")
	
            

		
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


