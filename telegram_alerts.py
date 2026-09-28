import logging
from aiogram import Bot

BOT_TOKEN = "8928813389:AAH3YndQddjn5l5aXN_wFVTaO4_CxFmnYA4"
CHAT_ID = 997497221  # Твой числовой ID


async def send_voltage_alert(voltage_value: float, sensor_id: str = "Sensor-01"):
    """
    Отправляет экстренное сообщение в Telegram и корректно закрывает сессию.
    """
    bot = Bot(token=BOT_TOKEN)
    message = (
        f"⚠️ **ВНИМАНИЕ: СКАЧОК НАПРЯЖЕНИЯ!** ⚠️\n\n"
        f"🔌 **Устройство:** `{sensor_id}`\n"
        f"⚡ **Текущее значение:** `{voltage_value:.1f} V`\n"
        f"🚨 **Статус:** Превышение допустимого порога!"
    )
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка отправки Telegram-алерта: {e}")
    finally:
        # Обязательно закрываем сессию aiohttp, чтобы не было Unclosed client session
        await bot.session.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(send_voltage_alert(247.5))
