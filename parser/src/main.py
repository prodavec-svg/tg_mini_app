import os
import time
import logging
import requests
import psycopg2
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Список акций для парсинга
TICKERS = ["SBER", "GAZP", "YNDX", "LKOH", "GMKN", "ROSN", "NVTK", "TATN"]


def get_price(ticker: str) -> float | None:
    """Получить текущую цену акции с MOEX ISS"""
    url = (
        f"https://iss.moex.com/iss/engines/stock/markets/shares/"
        f"boards/TQBR/securities/{ticker}.json"
        f"?iss.meta=off&iss.only=marketdata&marketdata.columns=SECID,LAST"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        rows = data.get("marketdata", {}).get("data", [])
        if rows and rows[0][1] is not None:
            return float(rows[0][1])
        else:
            logger.warning(f"{ticker}: цена недоступна (торги закрыты?)")
            return None

    except requests.RequestException as e:
        logger.error(f"{ticker}: ошибка запроса — {e}")
        return None


def save_prices(prices: list[dict]):
    """Сохранить список цен в PostgreSQL"""
    if not prices:
        logger.info("Нет данных для сохранения")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.executemany(
            "INSERT INTO prices (ticker, price, timestamp) VALUES (%s, %s, %s)",
            [(p["ticker"], p["price"], p["timestamp"]) for p in prices]
        )
        conn.commit()
        logger.info(f"Сохранено {len(prices)} записей в БД")

    except Exception as e:
        logger.error(f"Ошибка сохранения в БД: {e}")

    finally:
        if conn:
            cur.close()
            conn.close()


def job():
    """Основная задача: получить цены и сохранить в БД"""
    logger.info("Запуск парсинга...")
    timestamp = datetime.utcnow()
    prices = []

    for ticker in TICKERS:
        price = get_price(ticker)
        if price is not None:
            prices.append({
                "ticker": ticker,
                "price": price,
                "timestamp": timestamp
            })
            logger.info(f"{ticker}: {price} ₽")

    save_prices(prices)
    logger.info("Парсинг завершён\n")


if __name__ == "__main__":
    logger.info("Парсер запущен. Первый запуск сейчас, далее каждый час.")
    job()  # запуск сразу при старте

    schedule.every(1).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)