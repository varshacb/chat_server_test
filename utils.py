import asyncio
import websockets

from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect,Depends,Request
from uuid import uuid4
import multiprocessing
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from dotenv import load_dotenv

async def connect_to_master(port):
    uri = f"ws://localhost:5000/ws/0"  # WebSocket endpoint of the master server
    async with websockets.connect(uri) as websocket:
        await websocket.send(f"Hello from server instance running on port {port}!")
        response = await websocket.recv()
        print(f"Response from master server: {response}")

app = FastAPI()


# Example usage for three server instances
async def main():
    tasks = []
    for port in [8000, 8001, 8002]:
        tasks.append(connect_to_master(port))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())



# from fastapi import FastAPI
# import uvicorn
# import multiprocessing

# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# def run_server(port):
#     uvicorn.run(app, host="127.0.0.1", port=port)

# if __name__ == "__main__":
#     processes = []
#     ports = [8001, 8002] # List of ports for each instance

#     for port in ports:
#         process = multiprocessing.Process(target=run_server, args=(port,))
#         process.start()
#         processes.append(process)

#     for process in processes:
#         process.join()
