from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class AssetResponse(BaseModel):
    """Схема акции"""
    id: str
    name: str
    ticker: str
    price: float
    type: str = "stock"

class ActivePosition(BaseModel):
    """Схема активной позиции"""
    id: int
    hypothesisId: int
    ticker: str
    direction: str
    quantity: int
    duration: int
    priceOpen: float

class CompletedPosition(BaseModel):
    """Схема завершенной позиции"""
    id: int
    ticker: str
    direction: str
    quantity: int
    priceOpen: float
    priceClose: float
    result: float

class UserResponse(BaseModel):
    """Схема пользователя"""
    balance: float
    active: List[ActivePosition]
    completed: List[CompletedPosition]

class PositionRequest(BaseModel):
    """Схема запроса позиции"""
    assetId: str
    direction: str = Field(..., pattern="^(up|down)$")
    quantity: int = Field(..., gt=0)
    duration: int = Field(..., gt=0)

class HypothesisRequest(BaseModel):
    """Схема запроса гипотезы"""
    positions: List[PositionRequest]

class HypothesisResponse(BaseModel):
    """Схема ответа при создании гипотезы"""
    newBalance: float