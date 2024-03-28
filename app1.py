from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import asyncio
import os
import secrets
import multiprocessing
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")
SECRET_KEY = "bkhkjpo"

# Create a multiprocessing semaphore for inter-process synchronization


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket):
        tasks = [connection.send_text(message) for connection in self.active_connections if connection != websocket]
        await asyncio.gather(*tasks)

connection_manager = ConnectionManager()

def generate_session_id():
    return secrets.token_hex(16)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "X-Backend-Port"
    return response

@app.get("/")
async def home(request: Request):
    server_port = os.environ.get("PORT")
    # session = request.session
    # session_id = generate_session_id()
    # session["session_id"] = session_id
    # session["username"] = "client#"
    return templates.TemplateResponse("index.html", {"request": request, "port": server_port})

async def wait_and_connect(websocket: WebSocket):
    global shared_semaphore
    while True:
        if shared_semaphore.acquire():  # Non-blocking acquire
            try:
                await connection_manager.connect(websocket)
                break  # Connection established, exit loop
            except:
                shared_semaphore.release()  # Release semaphore on exception
                raise
            finally:
                shared_semaphore.release()

@app.websocket("/ws/{client_id}/{server_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, server_id: int):
    try:
        await wait_and_connect(websocket)
        while True:
            data = await websocket.receive_text()
            await connection_manager.send_personal_message(f"You: {data}", websocket)
            await connection_manager.broadcast(f"Client {client_id}#: {data}", websocket)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

def run_server(port):
    os.environ["PORT"] = str(port)
    
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    processes = []
    shared_semaphore = multiprocessing.Semaphore(1)
    ports = [8001, 8002, 8003]
    for port in ports:
        process = multiprocessing.Process(target=run_server, args=(port,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
