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
import os, json
import time
import secrets

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

f = open('server_connections.json')
data = json.load(f)
dict = data["server_connections"]
f.close()


def generate_session_id():
    return secrets.token_hex(16)  

def server_availability(request:Request):
    threshold = 2
    for key in dict:
         if(dict[key]<threshold):
              return True
    return False

def allocate_server():
    threshold = 2
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
    max_wait_time = 5 
    start_time = time.time()

    while True:
        if server_availability(request):
            # session = request.session
            # session_id = generate_session_id()
            # session["session_id"] = session_id
            # session["username"]="client#"
            conf = allocate_server()
            server = conf["server"]
            port = conf["port"]
            return RedirectResponse(url=server+f"/?var={port}", status_code=307)
        
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_wait_time:
            return {"no server available even after 5 minutes "}
        time.sleep(2) 



@app.get("/")
def read_index(request: Request):
    a=server_availability(request)
    print(a)
    if(a):
        # session = request.session
        # session_id = generate_session_id()
        # session["session_id"] = session_id
        # session["username"]="client#"
        conf = allocate_server()
        server = conf["server"]
        port = conf["port"]
        return RedirectResponse(url=server+f"/?var={port}", status_code=307)
    # return {"all servers are busy"}
    else:
        print("hi")
        msg = handle_client(request)
        return msg
    #     return{"msg":"hello"}
            

if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)