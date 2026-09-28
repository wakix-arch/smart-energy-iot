import os
import logging
from aiogram import Bot
from dotenv import load_dotenv

# Загружаем переменные из локального файла .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


async def send_voltage_alert(voltage_value: float, sensor_id: str = "Sensor-01"):
    """
    Отправляет экстренное сообщение в Telegram и корректно закрывает сессию.
    """
    if not BOT_TOKEN or not CHAT_ID:
        logging.error("Ошибка: BOT_TOKEN или CHAT_ID не найдены в файле .env!")
        return

    bot = Bot(token=BOT_TOKEN)
    message = (
        f"⚠️ **ВНИМАНИЕ: СКАЧОК НАПРЯЖЕНИЯ!** ⚠️\n\n"
        f"🔌 **Устройство:** `{sensor_id}`\n"
        f"⚡ **Текущее значение:** `{voltage_value:.1f} V`\n"
        f"🚨 **Статус:** Превышение допустимого порога!"
    )
    try:
        await bot.send_message(
            chat_id=int(CHAT_ID), text=message, parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Ошибка отправки Telegram-алерта: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(send_voltage_alert(247.5))
