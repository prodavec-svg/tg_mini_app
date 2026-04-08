from sqlalchemy import create_engine, event, NullPool, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    client_encoding='utf8',
    poolclass=NullPool
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """Функция для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def set_user_id_for_rls(db: Session, user_id: int):
    """Установка user_id для RLS"""
    db.execute(text(f"SET LOCAL app.user_id = '{user_id}'"))