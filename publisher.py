import time
import random
import json
import asyncio
from datetime import datetime
import paho.mqtt.client as mqtt
from telegram_alerts import send_voltage_alert

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smart_energy/sensor_01/data"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

print("⚡ Эмулятор датчика запущен. Нажмите Ctrl+C для остановки.")

while True:
    # 70% времени — норма (210-235V), 30% времени — скачок (170-189V или 240.1-260V)
    if random.random() > 0.3:
        voltage = round(random.uniform(210.0, 235.0), 1)
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
        print(
            f"🚨 АНОМАЛИЯ! Напряжение {voltage} V вышло за пределы нормы. Отправляем алерт..."
        )
        asyncio.run(send_voltage_alert(voltage_value=voltage))

    time.sleep(2)
