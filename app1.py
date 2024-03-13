# main.py

from fastapi import FastAPI, WebSocket,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import multiprocessing

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def broadcast(self, message: str):
        for connection in self.active_connections:
            asyncio.create_task(connection.send_text(message))

managers = [ConnectionManager() for _ in range(3)]  # Create 3 ConnectionManager instances
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):

	return templates.TemplateResponse("index.html", {"request" : request})

@app.websocket("/ws/{server_id}")
async def websocket_endpoint(websocket: WebSocket, server_id: int):
    await managers[server_id].connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            managers[server_id].broadcast(data)
    finally:
        managers[server_id].disconnect(websocket)

def run_server(port, server_id):
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    processes = []
    ports = [8000, 8001, 8002]  # Add more ports if needed

    for i, port in enumerate(ports):
        process = multiprocessing.Process(target=run_server, args=(port, i))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()
