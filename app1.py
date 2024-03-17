from typing import List
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect,Depends,Request
from uuid import uuid4
import multiprocessing


app = FastAPI()
templates = Jinja2Templates(directory="templates")

my_dict = {

         "http://localhost:8001":0,
         "http://localhost:8002":0,
         "http://localhost:8003":0

         }

@app.get("/")
def read_index(request: Request):
    threshold=2
    print(request)

    for index, (server, count) in enumerate(my_dict.items()):
        if count < threshold:
            my_dict[server] += 1
            print(f"{server}: {my_dict[server]}")
            port=8000+(index+1)
            return RedirectResponse(url=server+f"/target?var={port}", status_code=307)# Replace with the actual destination server URL

            # return templates.TemplateResponse(f"index{index}.html", {"request": request})

    return {"message": "All servers have reached the threshold"}



if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)