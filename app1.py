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

app = FastAPI()

ws_dict = {}

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"
ports=[8001,8002,8003]
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
async def websocket_endpoint(websocket: WebSocket,client_id: int):
	

	await connectionmanager.connect(websocket)

	try:
		print("printing:",ws_dict)
		while True:

			data = await websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
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

# def run_server(port):
# 	uvicorn.run(app, host="127.0.0.1", port = port)
		

@app.websocket("/ws2/{port}")
async def websocket_endpoint(websocket: WebSocket,port: int):

	await connectionmanager.connect(websocket)

	
# ws_dict={}
# async def connect_to_servers(port):
# 	for other_port in ports:
# 		if(other_port!=port):
# 				async with connect(f"ws://localhost:{other_port}/ws2/{port}") as websocket:
# 					ws_dict[other_port] = websocket
# 					while True:
# 						msg = await websocket.recv()
					
# asyncio.run(websocket_client())


#here i have to only recv and send it to my clients using that broadcast method
# when my client sends a msg i need to send to the other server instances using this dict



# def run_server(port):
# 	async def startup():
# 		await connect_to_servers(port,ports)
# 	app.startup_handlers.append(startup)
# 	uvicorn.run(app, host="127.0.0.1", port = port) 
#     # connect_to_servers(port,ports)  

	
	

async def startup_event():
    for port in ports:
        await connect_to_servers(port, ports)


app.add_event_handler("startup", startup_event)
		



	

if __name__ == "__main__":
		processes=[]
		
		for port in ports:
			# process = multiprocessing.Process(target = run_server,args = (port,))
			process = multiprocessing.Process(target=uvicorn.run, args=(app,), kwargs={"host": "127.0.0.1", "port": port})
			process.start()
			processes.append(process)

		for process in processes:
			process.join()






#     async def connect_to_servers():
#         for other_port in ports:
#             if other_port != port:
#                 uri = f"ws://localhost:{other_port}/ws2/{port}"  # WebSocket endpoint of other server instances
#                 async with connect(uri) as websocket:
#                     while True:
#                         try:
#                             data = await websocket.recv()
#                             await connectionmanager.broadcast(f"Client#: {data}", websocket)
#                             print(data)
#                         except:
#                             print("exception")
#                             break

#     asyncio.get_event_loop().run_until_complete(connect_to_servers())