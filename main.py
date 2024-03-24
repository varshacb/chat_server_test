from typing import List
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect,Depends,Request
from uuid import uuid4
import multiprocessing
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os, json,secrets,time
from starlette.middleware.sessions import SessionMiddleware



load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "xvbnjlai"


app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)



f = open('server_connections.json')
data = json.load(f)
dict = data["server_connections"]
f.close()


def generate_session_id():
    return secrets.token_hex(16)

def server_availability(request:Request):
    threshold = 2
    f = open('server_connections.json')
    data = json.load(f)
    dict = data["server_connections"]
    f.close()
    for key in dict:
         if(dict[key]<threshold):
              return True
    return False


def allocate_server():
    threshold = 2
    f = open('server_connections.json')
    data = json.load(f)
    dict = data["server_connections"]
    f.close()
    for index,(server,count) in enumerate(dict.items()):
        if count < threshold:
            port=8000+(index+1)
            dict[server] = count+1
            data["server_connections"] = dict
            f1 = open('server_connections.json','w')
            json.dump(data,f1)
            rd={"server":server,"port":port}
            return rd
        

def handle_client(request: Request):
    max_wait_time = 60
    start_time = time.time()
    elapsed_time = 0

    while elapsed_time < max_wait_time:
        if server_availability(request):
            session = request.session
            session_id = generate_session_id()
            session["session_id"] = session_id
            session["username"]="client#"
            conf = allocate_server()
            server = conf["server"]
            port = conf["port"]
            return RedirectResponse(url=server+f"/?var={port}", status_code=307)

        elapsed_time = time.time() - start_time
        if elapsed_time >= max_wait_time:
            session = request.session
            if "session_id" in session:
                session.pop("session_id")
                session.pop("username")
            return {"Session ended due to server unavailablity..Kindly start a new session later "}
        time.sleep(1)



@app.get("/")
def read_index(request: Request):

    if(server_availability(request)):
        session = request.session
        session_id = generate_session_id()
        session["session_id"] = session_id
        session["username"]="client#"
        conf = allocate_server()
        server = conf["server"]
        port = conf["port"]
        return RedirectResponse(url=server+f"/?var={port}", status_code=307)
    # return {"all servers are busy"}
    else:
        # print("hi")
        res = handle_client(request) 
        return res



if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)