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


app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "mysecretkey"
SESSION_COOKIE_NAME = "mycookie"

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie=SESSION_COOKIE_NAME)


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

connectionmanager = ConnectionManager()


def generate_session_id():
    return secrets.token_hex(16)  


@app.get("/")
async def home(request: Request):
	session = request.session
	session_id = generate_session_id()
	session["session_id"] = session_id
	session["username"]="client#"
	print(session.get("session_id"))
	port = request.query_params.get('var', '')
	dict={'port':port}
	return templates.TemplateResponse("index.html", {"request" : request, **dict})

@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket):

	await connectionmanager.connect(websocket)

	try:
		while True:

			data = await websocket.receive_text() 
			await connectionmanager.send_personal_message(f"You : {data}", websocket) 
			await connectionmanager.broadcast(f"Client #: {data}", websocket)

	except WebSocketDisconnect:
		connectionmanager.disconnect(websocket)
		await connectionmanager.broadcast(f"Client left the chat",websocket)


@app.post("/logout/{server_id}")
async def logout(request: Request,server_id:str):
		# s=server_id
		session=request.session
		print("hello")
		if "session_id" in session:
			session.pop("session_id")
			session.pop("username")

		string_build="http://localhost:"+server_id
		print(string_build)
		f = open('server_connections.json')
		data = json.load(f)
		dict = data["server_connections"]
		f.close()
		for key in dict:
			if(key == string_build):
				dict[key]-=1
		f1 = open('server_connections.json','w')
		print(dict)
		data['server_connections'] = dict
		json.dump(data,f1)
		print("done")


def run_server(port):
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








# the accept() fn. is called inside the connect fn. above
	# session_token = str(uuid4())
	# active_sessions={}
	# active_sessions[session_token] = websocket
	# active_sessions["client_id"]=client_id

# await connectionmanager.send_personal_message(f"Server : hi from server", websocket) # the server also replies with its msg to the client

#now these two msgs need to be received by the client (there we have the client side code in js in which onmessage event is triggered by the socket obj and the)

 # calling the connect fn in the above class (using the class obj ) which accepts the conn
	# session = Session(websocket,s_id)
	# sessions[session.id] = session
	# print(sessions)
	# print(active_sessions)
#  , client_id: int,s_id:str



# @app.get("/")
# def read_index(request: Request):
#     threshold=2
#     print(request)

#     for index, (server, count) in enumerate(my_dict.items()):
#         if count < threshold:
#             my_dict[server] += 1
#             print(f"{server}: {my_dict[server]}")
#             return templates.TemplateResponse(f"index{index}.html", {"request": request})

#     return {"message": "All servers have reached the threshold"}
        # else:
        #     return templates.TemplateResponse("index"+str(t)+".html", {"request" : request})