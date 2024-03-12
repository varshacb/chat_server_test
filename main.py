
import asyncio
from fastapi import FastAPI, WebSocket,uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a dictionary to store the WebSocket connections
connections = {}

# Define the WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Add the WebSocket connection to the dictionary
    connections[websocket] = True

    # Wait for messages from the client
    while True:
        data = await websocket.receive_text()

        # Send the message to all connected clients
        for connection in connections:
            await connection.send_text(data)

# Create a function to start a WebSocket server
async def start_websocket_server(host: str, port: int):
    # Create a new FastAPI application
    app = FastAPI()

    # Add the WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        # Add the WebSocket connection to the dictionary
        connections[websocket] = True

        # Wait for messages from the client
        while True:
            data = await websocket.receive_text()

            # Send the message to all connected clients
            for connection in connections:
                await connection.send_text(data)

    # Start the Uvicorn server
    await uvicorn.run(app, host=host, port=port)

# Create a function to start a WebSocket client
async def start_websocket_client(host: str, port: int):
    # Create a new WebSocket connection
    websocket = await websockets.connect(f"ws://{host}:{port}/ws")

    # Send a message to the server
    await websocket.send_text("Hello from the client!")

    # Wait for a message from the server
    data = await websocket.receive_text()

    # Print the message from the server
    print(data)

# Start the WebSocket servers and clients
asyncio.create_task(start_websocket_server("localhost", 8000))
asyncio.create_task(start_websocket_server("localhost", 8001))

asyncio.create_task(start_websocket_client("localhost", 8000))
asyncio.create_task(start_websocket_client("localhost", 8001))

# Wait for all tasks to complete
await asyncio.gather(*asyncio.all_tasks())