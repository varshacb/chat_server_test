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
from typing import Union

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")


# def 


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
            print("index"+str(index))
            port=8000+(index+1)
            data["server_connections"] = dict
            json.dump(data,f)
            f.close()
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
                 

    # return {"message": "All servers have reached the threshold"}



if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)


    from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import asyncio

app = FastAPI()

async def check_condition():
    # Simulated function that checks a condition (e.g., a database query)
    # Replace this with your actual condition-checking logic
    condition = False
    return condition

@app.get("/check_and_redirect")
async def check_and_redirect():
    max_wait_time = 300  # 5 minutes in seconds
    start_time = asyncio.get_event_loop().time()

    while True:
        if await check_condition():
            # Condition is met, redirect the client
            return RedirectResponse(url="/redirected_endpoint")

        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time >= max_wait_time:
            # Maximum wait time reached, return HTTP 204 No Content
            raise HTTPException(status_code=204)

        # Sleep for a short interval before checking again
        await asyncio.sleep(1)  # Sleep for 1 second before checking again

@app.get("/redirected_endpoint")
async def redirected_endpoint():
    return {"message": "Redirected successfully!"}
