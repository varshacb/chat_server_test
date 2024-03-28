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
import time
app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"
semaphore = asyncio.Semaphore(1)
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
		# print("inside broadcast method ")
		tasks = [connection.send_text(message) for connection in self.active_connections if connection != websocket]
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
	print("hi",server_port)
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	# print("hello"+session.get("session_id"))
	# port = request.query_params.get('var', '')
	# dict={'port':port}
	# semaphore-=1
	return templates.TemplateResponse("index.html", {"request" : request, "port": server_port})


@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket,client_id: int):
	
	try:
		await try_connection(websocket)  # await wait_and_connect(websocket)
		while True:

			data = await websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
			await connectionmanager.broadcast(f"Client {client_id}#: {data}", websocket)

	except WebSocketDisconnect:
		connectionmanager.disconnect(websocket)

	finally:
		semaphore.release()
		
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




# async with semaphore:
#         await connection_manager.connect(websocket)
#         try:
#             while True:
#                 data = await websocket.receive_text()
#                 await connection_manager.send_personal_message(f"You : {data}", websocket)
#                 await connection_manager.broadcast(f"Client {client_id}#: {data}", websocket)
#         except WebSocketDisconnect:
#             connection_manager.disconnect(websocket)
			


# set semaphore variable and if the server is busy send message to the client and ask it to wait handled it in 
# client side the waiting of the client if it can be like a timeout dont use sleep polling method that keeps checking the availability
# of the server and eventually allocates server or smthg maybe the client will hit the lh:80 if the semaphore is updated to a lesser value
			
# @app.post("/logout/{server_id}")
# async def logout(request: Request,server_id:str):
# 		# s=server_id
# 		session=request.session
# 		# print("hello")
# 		if "session_id" in session:
# 			session.pop("session_id")
# 			session.pop("username")

# 		server_string="http://localhost:"+server_id
# 		# print("the closed server:"+string_build)
# 		f = open('server_connections.json')
# 		data = json.load(f)
# 		dict = data["server_connections"]
# 		f.close()
# 		for key in dict:
# 			if(key == server_string):
# 				dict[key]-=1
# 		f1 = open('server_connections.json','w')
# 		# print(dict)
# 		data['server_connections'] = dict
# 		json.dump(data,f1)
		# print("done")
			

# async with semaphore:
	# 	await connectionmanager.connect(websocket)

# if await semaphore.acquire():
#         try:
#             print(f'Task {task_id} starting')
#             await asyncio.sleep(2)  # Simulating some asynchronous operation
#             print(f'Task {task_id} completed')
#         finally:
#             semaphore.release()  # Release the semaphore after the task completes
#     else:
#         print(f'Task {task_id} could not acquire semaphore, it is not available')

# async def try_connection(websocket:WebSocket):
# 	max_wait_time = 120
# 	start_time = time.time()
# 	elapsed_time = 0
# 	while elapsed_time < max_wait_time:
# 		if await semaphore.acquire():
# 			try:
# 				await connectionmanager.connect(websocket)
# 				return
# 			except:
# 				semaphore.release()
# 		elapsed_time = time.time() - start_time
# 		if(elapsed_time >= max_wait_time):
# 			return {"unable to acquire"}  


