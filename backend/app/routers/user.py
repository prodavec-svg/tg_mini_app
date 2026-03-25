from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/", response_model=schemas.UserResponse)
async def get_user(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получение данных пользователя"""

    # Получаем активные гипотезы
    active_hypotheses = db.query(models.Hypothesis).filter(
        and_(
            models.Hypothesis.user_id == current_user.id,
            models.Hypothesis.status == 'active'
        )
    ).all()

    # Получаем завершенные гипотезы
    completed_hypotheses = db.query(models.Hypothesis).filter(
        and_(
            models.Hypothesis.user_id == current_user.id,
            models.Hypothesis.status == 'completed'
        )
    ).all()

    # Формируем активные позиции
    active_positions = []
    for hypothesis in active_hypotheses:
        positions = db.query(models.Position).filter(
            models.Position.hypothesis_id == hypothesis.id
        ).all()

        for pos in positions:
            active_positions.append({
                "id": pos.id,
                "hypothesisId": hypothesis.id,
                "ticker": pos.ticker,
                "direction": pos.direction,
                "quantity": pos.quantity,
                "duration": pos.duration,
                "priceOpen": float(pos.price_open)
            })

    # Формируем завершенные позиции
    completed_positions = []
    for hypothesis in completed_hypotheses:
        positions = db.query(models.Position).filter(
            models.Position.hypothesis_id == hypothesis.id
        ).all()

        for pos in positions:
            if pos.price_close is not None and pos.result is not None:
                completed_positions.append({
                    "id": pos.id,
                    "ticker": pos.ticker,
                    "direction": pos.direction,
                    "quantity": pos.quantity,
                    "priceOpen": float(pos.price_open),
                    "priceClose": float(pos.price_close),
                    "result": float(pos.result)
                })

    return {
        "balance": float(current_user.balance),
        "active": active_positions,
        "completed": completed_positions
    }