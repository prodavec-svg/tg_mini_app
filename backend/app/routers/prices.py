from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app import models, schemas
from app.config import settings

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.post("/refresh", response_model=list[schemas.AssetResponse])
async def refresh_prices(db: Session = Depends(get_db)):
    """Обновление цен из таблицы prices"""
    assets = []

    for ticker, name in settings.COMPANIES.items():
        # Получаем последнюю цену по тикеру
        latest_price = db.query(models.Price).filter(
            models.Price.ticker == ticker
        ).order_by(desc(models.Price.timestamp)).first()

        price = float(latest_price.price) if latest_price else 0.0

        assets.append({
            "id": ticker,
            "name": name,
            "ticker": ticker,
            "price": price,
            "type": "stock"
        })

    return assets