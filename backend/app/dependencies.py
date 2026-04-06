from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from app.database import get_db, set_user_id_for_rls
from app import models
import os

async def get_current_user(
        x_telegram_user_id: int = Header(None, alias="X-Telegram-User-Id"),  # None вместо ...
        db: Session = Depends(get_db)
) -> models.User:
    """Получение текущего пользователя по Telegram user_id"""

    # ===== ТОЛЬКО ДЛЯ РАЗРАБОТКИ — закомментировать перед продакшеном =====
    if x_telegram_user_id is None:
        x_telegram_user_id = int(os.getenv("DEV_USER_ID", "123456789"))
    # ===== КОНЕЦ DEV-БЛОКА =====

    # ===== ПРОДАКШЕН — раскомментировать перед деплоем =====
    # if x_telegram_user_id is None:
    #     raise HTTPException(status_code=401, detail="X-Telegram-User-Id header is required")
    # =====

    set_user_id_for_rls(db, x_telegram_user_id)

    user = db.query(models.User).filter(models.User.id == x_telegram_user_id).first()

    if not user:
        user = models.User(
            id=x_telegram_user_id,
            username=None,
            balance=5000.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
