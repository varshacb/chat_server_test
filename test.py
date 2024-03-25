from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Your startup logic here (e.g., database connection)
    print("Connecting to database...")
    # ... (code to establish database connection)
    await asyncio.sleep(1)
    try:
        yield
    finally:
        # Your shutdown logic here (e.g., close database connection)
        # print("Closing database connection...")
        pass
        # ... (code to close database connection)

app = FastAPI(lifespan=lifespan)
# app= FastAPI()
    
# @app.event("startup")
# def fun():
#        print("hello")


@app.get("/")
def home():
     return {"hello:world"}

if __name__ == "__main__":
      
        uvicorn.run(app, host="127.0.0.1", port = 5000)
#         # startup_event()