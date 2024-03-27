import requests
from urllib.parse import urlparse, parse_qs
import websockets
import threading
import asyncio
import time

# 100 clients and 1000 messages and 3 server 
# server side , api use 

count = 100
with open("messages.txt",'r') as file:
     data = (file.read()).split("\n")
    #  print(data)


async def connect_to_websocket(server_addr,count):
    uri = f"ws://{server_addr}/ws/{count}/0"
    async with websockets.connect(uri) as websocket:
        # while True:
        try:
            for i in data:
                await websocket.send(i)
        except:
            print("reached execption")
                # response = await websocket.recv()
            # print(f"Received from server: {response}")
        # response = await websocket.recv()

def client_simulation(count):
    response = requests.get('http://localhost:80/') 
    server_addr=response.headers.get("X-Backend-Port")
    
    # parsed_url = urlparse(response.url)
    # query_parameters = parse_qs(parsed_url.query)
    # port = query_parameters['var'][0]
    # print(port)

    asyncio.run(connect_to_websocket(server_addr,count))

client_threads = []
for i in range(count):
    x = threading.Thread(target=client_simulation,args=(i,))
    start_time=time.time()
    x.start()
    client_threads.append(x)

# for t in client_threads:
#     t.start()
    

for t in client_threads:
    t.join()

end_time = time.time()

print(end_time-start_time)