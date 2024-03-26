import requests
from urllib.parse import urlparse, parse_qs
import websockets
import threading
import asyncio

count = 2
def client_simulation():
    response = requests.get('http://localhost:8000/') 

    print(response) 
    print(response.url)

    parsed_url = urlparse(response.url)

    query_parameters = parse_qs(parsed_url.query)

    port = query_parameters['var'][0]
    url= "ws://localhost:"+port+"/ws/0/0"
    print(url)

    async def connect_to_websocket():
        uri = "ws://localhost:"+port+"/ws/0/0" 
        async with websockets.connect(uri) as websocket:
            # while True:
                await websocket.send("Hello, FastAPI WebSocket!")
                response = await websocket.recv()
                print(f"Received from server: {response}")

    asyncio.get_event_loop().run_until_complete(connect_to_websocket())
  
    # await connect_to_websocket() threads use so that each client connection keeps running we can maybe logout
client_threads=[]
for i in range(count):
      x = threading.Thread(target=client_simulation)
      client_threads.append(x)
      x.start()

for t in client_threads:
    t.join()
# import requests
# from urllib.parse import urlparse, parse_qs
# import websockets
# import threading
# import asyncio
# import time

# count = 4
# with open("m.txt", 'r') as file:
#     data = (file.read()).split("\n")

# async def connect_to_websocket(port, count, timeout=10):
#     uri = f"ws://localhost:{port}/ws/{count}/0"
#     async with websockets.connect(uri) as websocket:
#         for i in data:
#             await websocket.send(i)

#         # Listen for messages continuously until timeout
#         while True:
#             try:
#                 response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
#                 print(f"Received from server: {response}")
#             except asyncio.TimeoutError:
#                 # print("No messages received within the timeout period.")
#                 break  # Exit the loop if timeout occurs

# def client_simulation(count, timeout=20):
#     response = requests.get('http://localhost:8000/')
#     parsed_url = urlparse(response.url)
#     query_parameters = parse_qs(parsed_url.query)
#     port = query_parameters['var'][0]
#     print(port)

#     asyncio.run(connect_to_websocket(port, count, timeout=timeout))

# client_threads = []
# for i in range(count):
#     x = threading.Thread(target=client_simulation, args=(i,))
#     client_threads.append(x)

# for t in client_threads:
#     t.start()
#     time.sleep(1)

# for t in client_threads:
#     t.join()