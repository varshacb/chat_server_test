import requests
import websockets
import threading
import asyncio
import time
import psutil


p = psutil.Process()

log_lock = threading.Lock()
count = 100
with open("message.txt",'r') as file:
     data = (file.read()).split("\n")


async def connect_to_websocket(server_addr,count):
    uri = f"ws://{server_addr}/ws/{count}/{server_addr[10::]}"
    retries = 20
    for attempt in range(retries+1):
        try:
            
        
            async with websockets.connect(uri) as websocket:
                for message in data:
                    await websocket.send(message)
                    t = time.strftime("%H:%M:%S")
                    with log_lock:
                        with open("test_log.txt", 'a') as log:
                            log.write(f"Client{count}      {t}       {server_addr[10::]}           {message} \n ")     
               
                break
        except Exception as e:
            if attempt < retries:
                t = time.strftime("%H:%M:%S")
                with log_lock:
                    with open("test_log.txt", 'a') as log:
                        log.write(f"Client{count}      {t}       {server_addr[10::]}          retrying\n ")
                await asyncio.sleep(1)  
    else:
        print(f"maximum retry attempts ({retries}) reached.failed to establish websocket connection")
                

def client_simulation(count):
    response = requests.get('http://localhost:80/') 
    server_addr = response.headers.get("X-Backend-Port")
    asyncio.run(connect_to_websocket(server_addr,count))

client_threads = []
for i in range(count):
    x = threading.Thread(target=client_simulation,args=(i,))
    start_time=time.time()
    x.start()
    client_threads.append(x)




for t in client_threads:
    t.join()

io = p.io_counters()
print("Read chars:",io.read_chars)
print("Write chars:", io.write_chars)



end_time = time.time()

print("load test time:",end_time-start_time)

