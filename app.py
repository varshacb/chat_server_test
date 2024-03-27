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
from main import alter_semaphore
import os
import asyncio
# from dotenv import load_dotenv

app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# load_dotenv()
# client = MongoClient("mongodb+srv://last:last1@pythoncluster.0zzvm.mongodb.net/")
# database = client["server_db"]
# collection_name = 'server_connections'
# collection=database[collection_name]

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
		print("inside broadcast method ")
		tasks = [connection.send_text(message) for connection in self.active_connections]
		await asyncio.gather(*tasks)	
			# if(connection == websocket):
			# 	continue
			# await connection.send_text(message)
	


connectionmanager = ConnectionManager()


def generate_session_id():
    return secrets.token_hex(16)  

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "X-Backend-Port"
    return response

@app.get("/")
async def home(request: Request):
	server_port = os.environ.get("PORT")
	print("hi",server_port)
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	# print("hello"+session.get("session_id"))
	# port = request.query_params.get('var', '')
	# dict={'port':port}
	return templates.TemplateResponse("index.html", {"request" : request, "port": server_port})

@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int):

	await connectionmanager.connect(websocket)

	try:
		while True:

			data = await websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
			await connectionmanager.broadcast(f"Client {client_id}#: {data}", websocket)

	except WebSocketDisconnect:
		connectionmanager.disconnect(websocket)
		# await connectionmanager.broadcast(f"Client left the chat",websocket)


@app.post("/logout/{server_id}")
async def logout(request: Request,server_id:str):
		# s=server_id
		session=request.session
		# print("hello")
		if "session_id" in session:
			session.pop("session_id")
			session.pop("username")

		server_string="http://localhost:"+server_id
		# print("the closed server:"+string_build)
		f = open('server_connections.json')
		data = json.load(f)
		dict = data["server_connections"]
		f.close()
		for key in dict:
			if(key == server_string):
				dict[key]-=1
		f1 = open('server_connections.json','w')
		# print(dict)
		data['server_connections'] = dict
		json.dump(data,f1)
		# print("done")


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






