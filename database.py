import sqlite3
from datetime import datetime

DB_NAME = "energy.db"


def init_db():
    """Создаёт таблицу для хранения логов аномалий, если она не существует."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                voltage REAL NOT NULL,
                current REAL NOT NULL,
                power REAL NOT NULL,
                alert_type TEXT NOT NULL
            )
        """)
        conn.commit()


def log_alert(voltage: float, current: float, power: float, alert_type: str):
    """Записывает данные о скачке напряжения в базу."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (timestamp, voltage, current, power, alert_type)
            VALUES (?, ?, ?, ?, ?)
        """,
            (now, voltage, current, power, alert_type),
        )
        conn.commit()


def get_recent_alerts(limit: int = 10):
    """Возвращает последние N записей об аномалиях."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, voltage, current, power, alert_type 
            FROM alerts 
            ORDER BY id DESC 
            LIMIT ?
        """,
            (limit,),
        )
        return cursor.fetchall()


if __name__ == "__main__":
    init_db()
    print("База данных успешно инициализирована!")
