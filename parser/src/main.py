import os
import logging
from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable

import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)



class PriceRecord:
    """Модель одной записи о цене акции."""

    def __init__(self, ticker: str, price: float, timestamp: datetime):
        self.ticker = ticker
        self.price = price
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return f"PriceRecord({self.ticker}, {self.price}, {self.timestamp})"




@runtime_checkable
class PriceFetcher(Protocol):
    """Отвечает только за получение цены одного тикера."""

    def fetch(self, ticker: str) -> float | None: ...


@runtime_checkable
class PriceRepository(Protocol):
    """Отвечает только за хранение записей о ценах."""

    def save_many(self, records: list[PriceRecord]) -> None: ...
    def delete_older_than(self, cutoff: datetime) -> int: ...



class MoexPriceFetcher:
    """Реализация PriceFetcher для Московской биржи (MOEX ISS)."""

    _BASE_URL = (
        "https://iss.moex.com/iss/engines/stock/markets/shares/"
        "boards/TQBR/securities/{ticker}.json"
        "?iss.meta=off&iss.only=marketdata&marketdata.columns=SECID,LAST"
    )

    def __init__(self, timeout: int = 10):
        self._timeout = timeout

    def fetch(self, ticker: str) -> float | None:
        url = self._BASE_URL.format(ticker=ticker)
        try:
            response = requests.get(url, timeout=self._timeout)
            response.raise_for_status()
            rows = response.json().get("marketdata", {}).get("data", [])
            if rows and rows[0][1] is not None:
                return float(rows[0][1])
            logger.warning("%s: цена недоступна (торги закрыты?)", ticker)
        except requests.RequestException as exc:
            logger.error("%s: ошибка запроса — %s", ticker, exc)
        return None


class PostgresPriceRepository:
    """Реализация PriceRepository поверх PostgreSQL (psycopg2)."""

    def __init__(self, dsn: str):
        self._dsn = dsn

    def _connect(self):
        return psycopg2.connect(self._dsn)

    def save_many(self, records: list[PriceRecord]) -> None:
        if not records:
            logger.info("Нет данных для сохранения")
            return

        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO prices (ticker, price, timestamp) VALUES (%s, %s, %s)",
                    [(r.ticker, r.price, r.timestamp) for r in records],
                )
            conn.commit()
            logger.info("Сохранено %d записей в БД", len(records))
        except Exception as exc:
            logger.error("Ошибка сохранения в БД: %s", exc)
        finally:
            if conn:
                conn.close()

    def delete_older_than(self, cutoff: datetime) -> int:
        """Удалить все записи старше cutoff. Возвращает количество удалённых строк."""
        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM prices WHERE timestamp < %s",
                    (cutoff,),
                )
                deleted = cur.rowcount
            conn.commit()
            logger.info("Удалено %d устаревших записей (старше %s)", deleted, cutoff)
            return deleted
        except Exception as exc:
            logger.error("Ошибка удаления устаревших записей: %s", exc)
            return 0
        finally:
            if conn:
                conn.close()


class PriceCollector:
    """
    Собирает цены по списку тикеров и сохраняет их через репозиторий.
    Зависит от абстракций, а не от конкретных классов (DIP).
    """

    def __init__(self, fetcher: PriceFetcher, repository: PriceRepository):
        self._fetcher = fetcher
        self._repository = repository

    def collect(self, tickers: list[str]) -> None:
        timestamp = datetime.utcnow()
        records: list[PriceRecord] = []

        for ticker in tickers:
            price = self._fetcher.fetch(ticker)
            if price is not None:
                records.append(PriceRecord(ticker, price, timestamp))
                logger.info("%s: %.2f ₽", ticker, price)

        self._repository.save_many(records)


class OldRecordsCleaner:
    """Отвечает только за очистку устаревших записей (SRP)."""

    def __init__(self, repository: PriceRepository, retention_days: int):
        self._repository = repository
        self._retention_days = retention_days

    def clean(self) -> int:
        cutoff = datetime.utcnow() - timedelta(days=self._retention_days)
        return self._repository.delete_older_than(cutoff)


class HypothesisSettler:
    """
    Находит активные гипотезы, срок которых истёк (created_at + duration <= now),
    вычисляет результат по цене из таблицы prices и обновляет:
      - positions.price_close, positions.result
      - hypotheses.status = 'closed', hypotheses.closed_at = now
      - users.balance += result
    """

    def __init__(self, dsn: str):
        self._dsn = dsn

    def _connect(self):
        return psycopg2.connect(self._dsn)

    def settle(self) -> None:
        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                # 1. Найти все активные гипотезы с истёкшим сроком
                cur.execute("""
                    SELECT
                        h.id        AS hypothesis_id,
                        h.user_id,
                        h.created_at,
                        p.id        AS position_id,
                        p.ticker,
                        p.direction,
                        p.quantity,
                        p.price_open,
                        p.duration
                    FROM hypotheses h
                    JOIN positions p ON p.hypothesis_id = h.id
                    WHERE h.status = 'active'
                      AND h.created_at + (p.duration * INTERVAL '1 day') <= NOW()
                """)
                rows = cur.fetchall()

            if not rows:
                logger.info("Нет завершённых гипотез для обработки")
                return

            logger.info("Найдено %d завершённых гипотез", len(rows))

            now = datetime.utcnow()

            for row in rows:
                (
                    hypothesis_id, user_id, created_at,
                    position_id, ticker, direction,
                    quantity, price_open, duration
                ) = row

                # 2. Получить актуальную цену закрытия из таблицы prices
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT price
                        FROM prices
                        WHERE ticker = %s
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """, (ticker,))
                    price_row = cur.fetchone()

                if price_row is None:
                    logger.warning(
                        "Гипотеза %d (тикер %s): цена закрытия не найдена в prices, пропускаю",
                        hypothesis_id, ticker
                    )
                    continue

                price_close = float(price_row[0])
                price_open_f = float(price_open)

                # 3. Рассчитать результат
                # LONG: прибыль = (цена_закрытия - цена_открытия) * количество
                # SHORT: прибыль = (цена_открытия - цена_закрытия) * количество
                if direction.lower() == "up":
                    result = (price_close - price_open_f) * quantity
                else:  # "down"
                    result = (price_open_f - price_close) * quantity

                logger.info(
                    "Гипотеза %d | %s | %s | open=%.2f close=%.2f qty=%d → result=%.2f",
                    hypothesis_id, ticker, direction,
                    price_open_f, price_close, quantity, result
                )

                with conn.cursor() as cur:
                    # 4. Обновить positions
                    cur.execute("""
                        UPDATE positions
                        SET price_close = %s,
                            result      = %s
                        WHERE id = %s
                    """, (price_close, result, position_id))

                    # 5. Закрыть гипотезу
                    cur.execute("""
                        UPDATE hypotheses
                        SET status    = 'closed',
                            closed_at = %s
                        WHERE id = %s
                    """, (now, hypothesis_id))

                    # 6. Пересчитать баланс пользователя
                    cur.execute("""
                        UPDATE users
                        SET balance = balance + %s
                        WHERE id = %s
                    """, (result, user_id))

            conn.commit()
            logger.info("Все завершённые гипотезы обработаны и закрыты")

        except Exception as exc:
            logger.error("Ошибка при закрытии гипотез: %s", exc)
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()


TICKERS = ["SBER", "GAZP", "YNDX", "LKOH", "GMKN", "ROSN", "NVTK", "TATN"]
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))


if __name__ == "__main__":
    dsn = os.environ["DATABASE_URL"]

    fetcher    = MoexPriceFetcher(timeout=10)
    repository = PostgresPriceRepository(dsn=dsn)
    collector  = PriceCollector(fetcher, repository)
    cleaner    = OldRecordsCleaner(repository, retention_days=RETENTION_DAYS)
    settler    = HypothesisSettler(dsn=dsn)

    logger.info("=== Запуск парсера ===")

    logger.info("--- Сбор цен ---")
    collector.collect(TICKERS)

    logger.info("--- Закрытие завершённых гипотез ---")
    settler.settle()

    logger.info("--- Очистка устаревших записей (старше %d дн.) ---", RETENTION_DAYS)
    cleaner.clean()

    logger.info("=== Готово ===")