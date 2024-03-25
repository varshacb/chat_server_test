from fastapi import FastAPI, WebSocket
import uvicorn
import multiprocessing

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

connections = []

@app.websocket("/ws/{server_port}")
async def websocket_endpoint(websocket: WebSocket,server_port:int):
    await websocket.accept()
    connections.append(websocket)
    # connections[server_port]=websocket
    print(connections)

    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            # Broadcast received message to all connections except sender
            for connection in connections:
                if connection != websocket:
                    await connection.send_text(data)
    finally:
        # connections.remove(websocket)
        print("entered finally block")

if __name__ == "__main__":
    
        uvicorn.run(app, host="127.0.0.1", port=5000)
