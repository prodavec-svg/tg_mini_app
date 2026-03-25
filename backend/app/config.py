import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")

    # Компании и их названия
    COMPANIES = {
        "SBER": "Сбербанк",
        "GAZP": "Газпром",
        "LKOH": "Лукойл",
        "GMKN": "Норникель",
        "ROSN": "Роснефть",
        "NVTK": "Новатэк",
        "TATN": "Татнефть"
    }

    # Начальный баланс пользователя
    INITIAL_BALANCE: float = 5000.0


settings = Settings()