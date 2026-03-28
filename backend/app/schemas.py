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
    assetId: str
    assetName: str
    ticker: str
    direction: str
    quantity: int
    duration: int
    openPrice: float   # фронт ждёт openPrice
    openTime: float
    endTime: float

class CompletedPosition(BaseModel):
    """Схема завершенной позиции"""
    id: int
    hypothesisId: int
    assetId: str
    assetName: str
    ticker: str
    direction: str
    quantity: int
    duration: int
    openPrice: float   # фронт ждёт openPrice
    closePrice: float  # фронт ждёт closePrice
    openTime: float
    endTime: float
    closeTime: float
    result: float
    status: str        # 'confirmed' | 'rejected'

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