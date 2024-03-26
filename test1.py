import requests
from urllib.parse import urlparse, parse_qs
import websockets
import threading
import asyncio
import time

# 100 clients and 1000 messages and 3 server 
# server side , api use 

count = 25
with open("messages.txt",'r') as file:
     data = (file.read()).split("\n")
    #  print(data)


async def connect_to_websocket(port,count):
    uri = f"ws://localhost:{port}/ws/{count}/0"
    async with websockets.connect(uri) as websocket:
        # while True:
        for i in data:
            await websocket.send(i)
            response = await websocket.recv()
            # print(f"Received from server: {response}")
        # response = await websocket.recv()

def client_simulation(count):
    response = requests.get('http://localhost:8000/') 
    print(response) 
    print(response.url)

    parsed_url = urlparse(response.url)
    query_parameters = parse_qs(parsed_url.query)
    port = query_parameters['var'][0]
    print(port)

    asyncio.run(connect_to_websocket(port,count))

client_threads = []
for i in range(count):
    x = threading.Thread(target=client_simulation,args=(i,))
    client_threads.append(x)

for t in client_threads:
    t.start()
    time.sleep(3)


for t in client_threads:
    t.join()