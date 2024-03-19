from pymongo import MongoClient
from typing import List
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect,Depends,Request
from uuid import uuid4

app = FastAPI()

client = MongoClient("mongodb+srv://last:last1@pythoncluster.0zzvm.mongodb.net/")
database = client["server_db"]
collection_name = 'server_connections'
collection=database[collection_name]

@app.get("/")
def index(request:Request):

    message = {
        "channel": "dev",
        "author": "cerami",
        "text": "Hello, world!"
    }

    result = collection.insert_one(message)
    print(result.inserted_id)
    # return render_template('index.html')

if __name__=='main':
    uvicorn.run(app, host="127.0.0.1", port=9000)
