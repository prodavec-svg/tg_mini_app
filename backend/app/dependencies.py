from fastapi import Header, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db, set_user_id_for_rls
from app import models

async def get_current_user(
    x_telegram_user_id: Optional[str] = Header(None, alias="X-Telegram-User-Id"),
    db: Session = Depends(get_db)
) -> models.User:
    if x_telegram_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-Telegram-User-Id header")
    
    try:
        user_id = int(x_telegram_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-Telegram-User-Id: must be an integer")
    
    if user_id <= 0:
        raise HTTPException(status_code=401, detail="Invalid user id: must be positive")
    
    set_user_id_for_rls(db, user_id)
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        user = models.User(id=user_id, username=None, balance=5000.0)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user
