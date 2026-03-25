from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base


class Price(Base):
    """Модель цен акций"""
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_prices_ticker_timestamp', 'ticker', 'timestamp'),
    )


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # Telegram user_id
    username = Column(String, nullable=True)
    balance = Column(Numeric(15, 2), default=5000.0, nullable=False)


class Hypothesis(Base):
    """Модель гипотезы"""
    __tablename__ = "hypotheses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String, default='active', nullable=False)  # active или completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)


class Position(Base):
    """Модель позиции"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    hypothesis_id = Column(Integer, ForeignKey('hypotheses.id'), nullable=False)
    ticker = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # up или down
    quantity = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # в минутах
    price_open = Column(Numeric(15, 2), nullable=False)
    price_close = Column(Numeric(15, 2), nullable=True)
    result = Column(Numeric(15, 2), nullable=True)