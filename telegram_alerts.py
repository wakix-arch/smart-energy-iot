import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


async def send_voltage_alert(voltage: float, current: float, power: float):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ BOT_TOKEN или CHAT_ID не найдены в файле .env!")
        return

    bot = Bot(token=BOT_TOKEN)

    alert_type = "ВЫСОКОЕ НАПРЯЖЕНИЕ 📈" if voltage > 240.0 else "НИЗКОЕ НАПРЯЖЕНИЕ 📉"

    message = (
        f"🚨 <b>ВНИМАНИЕ! СКАЧОК НАПРЯЖЕНИЯ!</b>\n"
        f"Тип: <b>{alert_type}</b>\n\n"
        f"⚡ <b>Напряжение:</b> {voltage} V\n"
        f"🔌 <b>Ток:</b> {current} A\n"
        f"💡 <b>Мощность:</b> {power} кВт\n\n"
        f"💾 <i>Запись автоматически сохранена в локальную SQLite БД.</i>"
    )

    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")
    finally:
        await bot.session.close()
