from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FoundApp API", "version": "1.0.0"}

@app.get("/ping")
def ping():
    return {"code": 0, "data": "pong"}
