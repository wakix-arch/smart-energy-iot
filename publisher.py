import time
import random
import json
import asyncio
from datetime import datetime
import paho.mqtt.client as mqtt

from telegram_alerts import send_voltage_alert
from database import init_db, log_alert

# Инициализируем БД при старте
init_db()

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smart_energy/sensor_01/data"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT, 60)

print("⚡ Эмулятор датчика запущен. Нажмите Ctrl+C для остановки.")

while True:
    # 85% времени — полная норма (215-235V)
    # 15% времени — редкие скачки (170-189V или 240.1-260V)
    if random.random() > 0.15:
        voltage = round(random.uniform(215.0, 235.0), 1)
    else:
        voltage = round(
            random.choice([random.uniform(170.0, 189.0), random.uniform(240.1, 260.0)]),
            1,
        )

    current = round(random.uniform(1.0, 15.0), 2)
    power = round((voltage * current) / 1000, 3)  # кВт

    payload = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "voltage": voltage,
        "current": current,
        "power": power,
    }

    # Отправляем JSON в MQTT
    client.publish(TOPIC, json.dumps(payload))
    print(f"📡 Данные отправлены: {payload}")

    # Проверка на аномалию (меньше 190V или больше 240V)
    if voltage < 190.0 or voltage > 240.0:
        alert_type = "HIGH_VOLTAGE" if voltage > 240.0 else "LOW_VOLTAGE"
        print(
            f"🚨 АНОМАЛИЯ ({alert_type})! Напряжение {voltage} V. Сохраняем в БД и шлём алерт..."
        )

        # 1. Запись аномалии в локальную SQLite БД
        log_alert(voltage=voltage, current=current, power=power, alert_type=alert_type)

        # 2. Асинхронная отправка в Telegram
        asyncio.run(send_voltage_alert(voltage=voltage, current=current, power=power))

    time.sleep(2)
