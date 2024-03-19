from fastapi import FastAPI, Request, Response, Depends
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Secret key for session encryption
SECRET_KEY = "mysecretkey"
# Name of the session cookie
SESSION_COOKIE_NAME = "mycookie"

# Initialize session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie=SESSION_COOKIE_NAME)

# Example route to set session data
@app.get("/set-session/")
async def set_session_data(request: Request):
    session = request.session
    session["user_id"] = 123
    session["username"] = "user123"
    return {"message": "Session data set successfully"}

# Example route to retrieve session data
@app.get("/get-session/")
async def get_session_data(request: Request):
    session = request.session
    user_id = session.get("user_id")
    username = session.get("username")
    return {"user_id": user_id, "username": username}

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


    # Yes, the SessionMiddleware in FastAPI automatically generates a unique session ID for each client session.
    # This session ID is stored as a cookie in the client's browser. The session ID is used to associate the
    # session data with the client's requests, allowing you to maintain state across multiple requests for the same client.
    # You can access this session ID using the request.session._session_id attribute if needed.

    # Request.session._session_id