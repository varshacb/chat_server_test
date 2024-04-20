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
import threading
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
	print(multiprocessing.get_start_method())

	
	server_port = os.environ.get("PORT")
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	
	return templates.TemplateResponse("index.html", {"request" : request, "port": server_port})


@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int,server_id:str):	
	
	try:
		await try_connection(websocket)
		message_count = 0 
		start_time = time.time()
		while True:	
			message_count += 1
			data = await websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
			await connectionmanager.broadcast(f"Client {client_id}#: {data}", websocket)

	except WebSocketDisconnect:
		end_time = time.time() 
		response_time = (end_time - start_time)/message_count
		throughput = message_count/(end_time-start_time)
		with log_lock:
			with open("server_log.txt",'a') as log:
				log.write(f"Server id :{server_id}      response time : {response_time:.2f}          throughput : {throughput:.2f} \n")
		connectionmanager.disconnect(websocket)

	finally:
		semaphore.release()


		
def run_server(port):
	os.environ["PORT"]=str(port)
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








# tedex