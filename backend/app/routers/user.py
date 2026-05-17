from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("", response_model=schemas.UserResponse)
@router.get("/", response_model=schemas.UserResponse)
async def get_user(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получение данных пользователя"""

    active_hypotheses = db.query(models.Hypothesis).filter(
        and_(
            models.Hypothesis.user_id == current_user.id,
            models.Hypothesis.status == 'active'
        )
    ).all()

    completed_hypotheses = db.query(models.Hypothesis).filter(
        and_(
            models.Hypothesis.user_id == current_user.id,
            models.Hypothesis.status == 'closed'
        )
    ).all()

    active_positions = []
    for hypothesis in active_hypotheses:
        positions = db.query(models.Position).filter(
            models.Position.hypothesis_id == hypothesis.id
        ).all()

        for pos in positions:
            open_ts = hypothesis.created_at.timestamp() * 1000
            end_ts = open_ts + pos.duration * 24 * 60 * 60 * 1000

            active_positions.append({
                "id": pos.id,
                "hypothesisId": hypothesis.id,
                "assetId": pos.ticker,
                "assetName": pos.ticker,      # ticker как имя, т.к. отдельного поля name нет
                "ticker": pos.ticker,
                "direction": pos.direction,
                "quantity": pos.quantity,
                "duration": pos.duration,
                "openPrice": float(pos.price_open),  # фронт ждёт openPrice
                "openTime": open_ts,
                "endTime": end_ts,
            })

    completed_positions = []
    for hypothesis in completed_hypotheses:
        positions = db.query(models.Position).filter(
            models.Position.hypothesis_id == hypothesis.id
        ).all()

        for pos in positions:
            if pos.price_close is None or pos.result is None:
                continue

            open_ts = hypothesis.created_at.timestamp() * 1000
            end_ts = open_ts + pos.duration * 24 * 60 * 60 * 1000
            close_ts = hypothesis.closed_at.timestamp() * 1000 if hypothesis.closed_at else end_ts

            completed_positions.append({
                "id": pos.id,
                "hypothesisId": hypothesis.id,
                "assetId": pos.ticker,
                "assetName": pos.ticker,
                "ticker": pos.ticker,
                "direction": pos.direction,
                "quantity": pos.quantity,
                "duration": pos.duration,
                "openPrice": float(pos.price_open),
                "closePrice": float(pos.price_close),
                "openTime": open_ts,
                "endTime": end_ts,
                "closeTime": close_ts,
                "result": float(pos.result),
                "status": "confirmed" if float(pos.result) >= 0 else "rejected",
            })

    return {
        "balance": float(current_user.balance),
        "active": active_positions,
        "completed": completed_positions
    }
