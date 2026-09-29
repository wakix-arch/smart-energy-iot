import json
import sqlite3
import time
import pandas as pd
import paho.mqtt.client as mqtt
import streamlit as st
from database import DB_NAME, init_db

init_db()

st.set_page_config(page_title="Smart Energy Dashboard", page_icon="⚡", layout="wide")

st.title("⚡ Мониторинг энергосети в реальном времени")


# Глобальный кэшированный клиент и хранилище
@st.cache_resource
def setup_mqtt_and_store():
    store = {
        "timestamp": "--:--:--",
        "voltage": 220.0,
        "current": 0.0,
        "power": 0.0,
    }

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            store["timestamp"] = payload.get("timestamp", "--:--:--")
            store["voltage"] = payload.get("voltage", 220.0)
            store["current"] = payload.get("current", 0.0)
            store["power"] = payload.get("power", 0.0)
        except Exception as e:
            print(f"Ошибка MQTT: {e}")

    BROKER = "broker.hivemq.com"
    PORT = 1883
    TOPIC = "smart_energy/sensor_01/data"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC)
    client.loop_start()

    return store


data_store = setup_mqtt_and_store()

tab1, tab2 = st.tabs(["📡 Реальное время", "🚨 История аномалий (SQLite)"])

with tab1:
    st.subheader("Текущие показатели датчика")

    # Создаём пустой контейнер для живых метрик
    metrics_container = st.empty()

with tab2:
    st.subheader("Журнал зафиксированных аномалий")

    def load_alerts():
        try:
            with sqlite3.connect(DB_NAME) as conn:
                query = """
                    SELECT 
                        id AS 'ID',
                        timestamp AS 'Время',
                        voltage AS 'Напряжение (V)',
                        current AS 'Ток (A)',
                        power AS 'Мощность (кВт)',
                        alert_type AS 'Тип аномалии'
                    FROM alerts 
                    ORDER BY id DESC
                """
                return pd.read_sql_query(query, conn)
        except Exception as e:
            st.error(f"Ошибка чтения БД: {e}")
            return pd.DataFrame()

    df_alerts = load_alerts()
    if not df_alerts.empty:
        st.write(f"Всего аномалий в базе: **{len(df_alerts)}**")
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)
    else:
        st.info("В базе данных пока нет записей о скачках.")

    if st.button("🔄 Обновить историю"):
        st.rerun()

# Автоматическое прямое обновление карточек метрик во вкладке 1
while True:
    with metrics_container.container():
        voltage_val = data_store["voltage"]
        current_val = data_store["current"]
        power_val = data_store["power"]
        time_val = data_store["timestamp"]

        col1, col2, col3 = st.columns(3)

        if voltage_val < 190.0 or voltage_val > 240.0:
            col1.metric(
                "⚡ Напряжение", f"{voltage_val} V", "АНОМАЛИЯ", delta_color="inverse"
            )
        else:
            col1.metric("⚡ Напряжение", f"{voltage_val} V", "Норма")

        col2.metric("🔌 Ток", f"{current_val} A")
        col3.metric("💡 Мощность", f"{power_val} кВт")

        st.caption(f"Последнее обновление: {time_val}")

    time.sleep(1)
