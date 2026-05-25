import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assets, user, hypotheses, prices

from app.config import settings

app = FastAPI(
    title="Trading Simulator API",
    description="Telegram Mini App Trading Simulator",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
