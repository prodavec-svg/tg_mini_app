from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal
from app.database import get_db, set_user_id_for_rls
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/hypotheses", tags=["hypotheses"])


@router.post("/", response_model=schemas.HypothesisResponse)
async def create_hypothesis(
        request: schemas.HypothesisRequest,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Создание новой гипотезы"""

    # Проверяем баланс пользователя
    total_cost = Decimal('0')
    positions_data = []

    for pos_request in request.positions:
        # Получаем актуальную цену акции
        latest_price = db.query(models.Price).filter(
            models.Price.ticker == pos_request.assetId
        ).order_by(desc(models.Price.timestamp)).first()

        if not latest_price:
            raise HTTPException(
                status_code=400,
                detail=f"Asset {pos_request.assetId} not found"
            )

        # Рассчитываем стоимость позиции
        cost = latest_price.price * pos_request.quantity
        total_cost += cost

        positions_data.append({
            "ticker": pos_request.assetId,
            "direction": pos_request.direction,
            "quantity": pos_request.quantity,
            "duration": pos_request.duration,
            "price_open": latest_price.price
        })

    # Проверяем достаточно ли средств
    if total_cost > current_user.balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: {total_cost}, Available: {current_user.balance}"
        )

    # Начинаем транзакцию
    try:
        # Списываем средства с баланса
        current_user.balance -= total_cost
        db.add(current_user)

        # Создаем новую гипотезу
        hypothesis = models.Hypothesis(
            user_id=current_user.id,
            status='active'
        )
        db.add(hypothesis)
        db.flush()  # Получаем ID гипотезы

        # Создаем позиции
        for pos_data in positions_data:
            position = models.Position(
                hypothesis_id=hypothesis.id,
                **pos_data
            )
            db.add(position)

        db.commit()

        return {"newBalance": float(current_user.balance)}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))