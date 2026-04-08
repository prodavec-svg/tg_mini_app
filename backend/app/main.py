import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assets, user, hypotheses, prices

app = FastAPI(
    title="Trading Simulator API",
    description="Telegram Mini App Trading Simulator",
    version="1.0.0"
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assets.router)
app.include_router(user.router)
app.include_router(hypotheses.router)
app.include_router(prices.router)

@app.get("/")
async def root():
    return {
        "message": "Trading Simulator API",
        "version": "1.0.0",
        "endpoints": ["/api/assets", "/api/user", "/api/hypotheses", "/api/prices/refresh"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}