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
import os

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

MONGO_URI = os.environ.get('MONGO_URI')

client = MongoClient(MONGO_URI)
database = client["server_db"]
collection_name = 'server_connections'
collection=database[collection_name]

@app.get("/")
def read_index(request: Request):

    threshold=2
    server_connections = collection.find_one()
    server_dict=server_connections.get("server")
    for index,(server,count) in enumerate(server_dict.items()):
        if count < threshold:
            server_dict[server]=count+1
            # print("done")
            port=8000+(index+1)
            result = collection.update_one(
                    {"_id": ObjectId("65f9a73270de3cd09a3770b4")},
                    {"$set": {"server": server_dict}}
                    )
            return RedirectResponse(url=server+f"/?var={port}", status_code=307)
    return {"message": "All servers have reached the threshold"}



if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)