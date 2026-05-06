from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FoundApp API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"code": 0, "data": "pong"}

@app.get("/")
async def root():
    return {"message": "FoundApp API", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    # Database init will be added when full app is restored
    pass
