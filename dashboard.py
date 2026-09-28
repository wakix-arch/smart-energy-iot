import json
import threading
import time
import pandas as pd
import paho.mqtt.client as mqtt
import plotly.express as px
import streamlit as st

# Глобальное хранилище данных
if "data_history" not in st.session_state:
    st.session_state.data_history = []

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "astana/smart_tech/energy_meter"

# Настройка страницы Streamlit
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")
st.title("⚡ Smart Energy & IoT Monitoring System")


# Колбэк при получении нового сообщения
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        st.session_state.data_history.append(payload)
        # Храним только последние 30 измерений
        if len(st.session_state.data_history) > 30:
            st.session_state.data_history.pop(0)
    except Exception as e:
        pass


# Запуск MQTT-клиента в отдельном потоке
@st.cache_resource
def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC)
    client.loop_start()
    return client


start_mqtt()

# Создаем плейсхолдеры для обновления UI
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
chart_placeholder = st.empty()

# Автообновление страницы раз в секунду
while True:
    if st.session_state.data_history:
        df = pd.DataFrame(st.session_state.data_history)
        latest = df.iloc[-1]

        # Карточки метрик (KPI)
        kpi_col1.metric(
            "Напряжение (В)",
            f"{latest['voltage']} V",
            delta=round(latest["voltage"] - 220, 1),
        )
        kpi_col2.metric("Сила тока (А)", f"{latest['current']} A")
        kpi_col3.metric("Мощность (кВт)", f"{latest['power']} kW")

        # Проверка аномалий / алерты
        if latest["voltage"] > 240.0:
            st.warning(f"⚠️ Скачок напряжения! Зафиксировано: {latest['voltage']} В")

        # График мощности в реальном времени
        fig = px.line(
            df,
            x="timestamp",
            y="power",
            title="Динамика потребления мощности (кВт)",
            markers=True,
        )
        chart_placeholder.plotly_chart(fig, use_container_width=True)

    time.sleep(1)
