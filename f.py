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
from websockets import connect
import asyncio

from contextlib import asynccontextmanager

app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


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
		for connection in self.active_connections:
			if(connection == websocket):
				continue
			await connection.send_text(message)
		# async with connect("ws://localhost:5000/ws") as websocket:
		# 	await websocket.send("Hello, Server 1!")
	
	async def broadcast_new(self, message: str):
		if len(self.active_connections)==0:
			print("no active connections")
            
		for connection in self.active_connections:
			await connection.send_text(message)
		# async with connect("ws://localhost:5000/ws") as websocket:
		# 	await websocket.send("Hello, Server 1!")
			
	async def send_to_servers(self,msg):
		for port in ws_dict:
			ws_dict[port].send(msg)
			print("done")

connectionmanager = ConnectionManager()
ws_dict={}

async def server_fn(port, other_port):
		print("hy2")
		async with connect(f"ws://localhost:{other_port}/ws2/{port}") as websocket:
			ws_dict[other_port] = websocket
			while True:
				msg = await websocket.recv()
				connectionmanager.broadcast_new(msg)
            # print(f"Received message from {other_port}: {msg}")
async def connect_to_servers(port, ports):
		print("hyyu")
		tasks = []
		for other_port in ports:
			if other_port != port:
				task = asyncio.create_task(server_fn(port, other_port))
				tasks.append(task)
		await asyncio.gather(*tasks)
		

def generate_session_id():
    return secrets.token_hex(16)  


@app.get("/")
async def home(request: Request):
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	# print("hello"+session.get("session_id"))
	port = request.query_params.get('var', '')
	dict={'port':port}
	return templates.TemplateResponse("index.html", {"request" : request, **dict})

@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int,server_id :int):

	await connectionmanager.connect(websocket)
	print(type(server_id))
	
	print("dictt",ws_dict)

	try:
		while True:

			data = await websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
			await connectionmanager.send_to_servers(data)
			# await connectionmanager.broadcast(f"Client {client_id}#: {data}", websocket)

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
		data['server_connections'] = dict
		json.dump(data,f1)
		



@asynccontextmanager
async def lifespan(app: FastAPI):
	print("Connecting to database...")
	await connect_to_servers(port, ports)
	# await asyncio.sleep(1)
	
	try:
		yield
	finally:
        # Your shutdown logic here (e.g., close database connection)
        # print("Closing database connection...")
		pass
        # ... (code to close database connection)

app = FastAPI(lifespan=lifespan)
@app.websocket("/ws2/{port}")
async def websocket_endpoint1(websocket: WebSocket,port: int):

	await connectionmanager.connect(websocket)

def run_server(port):
	
	uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
		processes=[]
		ports=[8001,8002,8003]
		for port in ports:
			process = multiprocessing.Process(target=run_server, args=(port,))
			process.start()
			processes.append(process)

		for process in processes:
			process.join()





