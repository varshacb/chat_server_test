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

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

f = open('server_connections.json')
data = json.load(f)
dict = data["server_connections"]

def server_availability():
    threshold = 2
    for key in dict:
         if(dict[key]<threshold):
              return True
    return False

def allocate_server(request: Request):
    threshold = 2
    f = open('server_connections.json','w')
    for index,(server,count) in enumerate(dict.items()):
        if count < threshold:
            port=8000+(index+1)
            dict[server] = count+1
            data["server_connections"] = dict
            f1 = open('server_connections.json','w')
            json.dump(data,f1)
            rd={"server":server,"port":port}
            return rd

def handle_client():
     print("waiting")


@app.get("/")
def read_index(request: Request):
            if(server_availability()):
                conf = allocate_server(request)
                server = conf["server"]
                port = conf["port"]
                return RedirectResponse(url=server+f"/?var={port}", status_code=307)
            else:
                    handle_client()
                    

if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)