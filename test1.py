import requests
from urllib.parse import urlparse, parse_qs
import websockets
import threading
import asyncio
import time

# 100 clients, 1000 messages and 3 servers

count = 100
with open("message.txt",'r') as file:
     data = (file.read()).split("\n")
    #  print(data)


async def connect_to_websocket(server_addr,count):
    uri = f"ws://{server_addr}/ws/{count}/0"
    # ws = websockets.connect(uri)
    retries = 20
    for attempt in range(retries +1):
        try:
            async with websockets.connect(uri) as websocket:
                for message in data:
                    await websocket.send(message)
                # print(f"websocket connection established on attempt{attempt+1}")
                break
        except Exception as e:
            # print(f"Failed to connect to WebSocket on attempt {attempt + 1}: {e}")
            if attempt < retries:
                # print("Retrying")
                await asyncio.sleep(1)  
    else:
        print(f"maximum retry attempts ({retries}) reached.failed to establish websocket connection")
                

def client_simulation(count):
    response = requests.get('http://localhost:80/') 
    server_addr=response.headers.get("X-Backend-Port")
    asyncio.run(connect_to_websocket(server_addr,count))

client_threads = []
for i in range(count):
    x = threading.Thread(target=client_simulation,args=(i,))
    start_time=time.time()
    x.start()
    client_threads.append(x)



for t in client_threads:
    t.join()

end_time = time.time()

print(end_time-start_time)

