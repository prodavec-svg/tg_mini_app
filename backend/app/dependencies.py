from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from app.database import get_db, set_user_id_for_rls
from app import models


async def get_current_user(
        x_telegram_user_id: int = Header(..., alias="X-Telegram-User-Id"),
        db: Session = Depends(get_db)
) -> models.User:
    """Получение текущего пользователя по Telegram user_id"""
    # Устанавливаем user_id для RLS
    set_user_id_for_rls(db, x_telegram_user_id)

    # Ищем пользователя
    user = db.query(models.User).filter(models.User.id == x_telegram_user_id).first()

    # Если пользователь не найден, создаем нового
    if not user:
        user = models.User(
            id=x_telegram_user_id,
            username=None,  # Можно будет добавить позже из Telegram данных
            balance=5000.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user