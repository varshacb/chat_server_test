import asyncio
import json
import multiprocessing
import secrets
from typing import List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from websockets import connect

app = FastAPI()

templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

class ConnectionManager:
    def __init__(self):
        self.active_client_connections: List[WebSocket] = []
        self.server_connections = {}  # Store WebSocket servers for each instance

    async def connect_client(self, websocket: WebSocket):
        await websocket.accept()
        self.active_client_connections.append(websocket)

    async def connect_to_other_servers(self, server_id: str):
        for other_server_id, ws_server in self.server_connections.items():
            if other_server_id != server_id:
                uri = f"ws://localhost:8000/server_ws/{other_server_id}"  # WebSocket endpoint of other server instances
                if uri not in self.server_connections.values():  # Check if connection already exists
                    async with connect(uri) as websocket:
                        self.server_connections[other_server_id] = websocket
                        await self.forward_messages(websocket)

    async def forward_messages(self, websocket: WebSocket):
        while True:
            try:
                data = await websocket.recv()
                # Process received data from other servers as needed
            except websockets.ConnectionClosed:
                break

    async def send_to_other_servers(self, message: str, sender_server_id: str):
        for other_server_id, ws_server in self.server_connections.items():
            if other_server_id != sender_server_id:
                await ws_server.send(message)

    def disconnect_client(self, websocket: WebSocket):
        self.active_client_connections.remove(websocket)

    async def broadcast_to_clients(self, message: str):
        for websocket in self.active_client_connections:
            await websocket.send_text(message)

connection_manager = ConnectionManager()

def generate_session_id():
    return secrets.token_hex(16)

@app.get("/")
async def home(request: Request):
    session = request.session
    session_id = generate_session_id()
    session["session_id"] = session_id
    session["username"] = "client#"
    port = request.query_params.get('var', '')
    dict = {'port': port}
    return templates.TemplateResponse("index.html", {"request": request, **dict})

@app.websocket("/client_ws")
async def client_websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect_client(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.send_to_other_servers(f"Client message: {data}", sender_server_id="client")
            await connection_manager.broadcast_to_clients(f"You (client): {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect_client(websocket)

@app.websocket("/server_ws/{server_id}")
async def server_websocket_endpoint(websocket: WebSocket, server_id: str):
    await websocket.accept()
    connection_manager.server_connections[server_id] = websocket
    await connection_manager.connect_to_other_servers(server_id)

def run_server(port):
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    processes = []
    ports = [8001, 8002, 8003]
    for port in ports:
        process = multiprocessing.Process(target=run_server, args=(port,))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()
