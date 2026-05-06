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

# Import routers
from app.routers import auth, user, match, chat, moments, wallet, trtc, utils

# Register routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(match.router)
app.include_router(chat.router)
app.include_router(moments.router)
app.include_router(wallet.router)
app.include_router(trtc.router)
app.include_router(utils.router)

@app.get("/ping")
async def ping():
    return {"code": 0, "data": "pong"}

@app.get("/")
async def root():
    return {"message": "FoundApp API", "version": "1.0.0"}
