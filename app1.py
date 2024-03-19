from typing import List
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect,Depends,Request
from uuid import uuid4
import multiprocessing
from pymongo import MongoClient
from pydantic import BaseModel


app = FastAPI()
templates = Jinja2Templates(directory="templates")
class Item(BaseModel):
    name: str


my_dict = {

         "http://localhost:8001":0,
         "http://localhost:8002":0,
         "http://localhost:8003":0

         }
client = MongoClient("mongodb+srv://last:last1@pythoncluster.0zzvm.mongodb.net/")
database = client["server_db"]
collection_name = 'server_connections'
collection=database[collection_name]

@app.get("/")
def read_index(request: Request):
    message = {
        "channel": "dev",
        "author": "cerami",
        "text": "Hello, world!"
    }

    result = collection.insert_one(message)
    print("hi"+ str(result.inserted_id))
    x = collection.find_one()

    print("hi"+ str(type(x)))

    threshold=2
    print(request)

    for index, (server, count) in enumerate(my_dict.items()):
        if count < threshold:
            my_dict[server] += 1
            print(f"{server}: {my_dict[server]}")
            port=8000+(index+1)
            return RedirectResponse(url=server+f"/?var={port}&my_dict={my_dict}", status_code=307)# Replace with the actual destination server URL

            # return templates.TemplateResponse(f"index{index}.html", {"request": request})

    return {"message": "All servers have reached the threshold"}



if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)