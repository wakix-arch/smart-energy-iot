# ⚡ Smart Energy IoT Monitoring & Alerting System

Легковесная IoT-система мониторинга электросети в реальном времени. Эмулирует показатели умных счетчиков электроэнергии, сохраняет историю аварийных скачков (высокое/низкое напряжение) в локальную базу данных SQLite, отображает живые метрики на дашборде Streamlit и отправляет мгновенные уведомления в Telegram.

---

## 📐 Архитектура системы

```text
                        ┌────────────────────────┐
                        │   publisher.py         │
                        │   (Эмулятор датчика)   │
                        └───────────┬────────────┘
                                    │
                                    │ (MQTT Publish / JSON)
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                          broker.hivemq.com                            │
│                 Топик: smart_energy/sensor_01/data                    │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
┌──────────────────────────────┐ ┌──────────────────────────────────────┐
│        dashboard.py          │ │          Фиксация аномалии           │
│   (Streamlit Real-Time DOM)  │ │ (Напряжение < 190V или > 240V)      │
└──────────────────────────────┘ └──────────────────┬───────────────────┘
                                                    │
                                     ┌──────────────┴──────────────┐
                                     │                             │
                                     ▼                             ▼
                      ┌──────────────────────────┐   ┌───────────────────────────┐
                      │       database.py        │   │    telegram_alerts.py    │
                      │   (SQLite: energy.db)    │   │   (Aiogram 3 / Async)     │
                      └──────────────────────────┘   └─────────────┬─────────────┘
                                                                   │
                                                                   ▼
                                                     ┌───────────────────────────┐
                                                     │      Клиент Telegram      │
                                                     └───────────────────────────┘
```

---

## 🛠️ Стек технологий

* **Язык программирования**: Python 3.10+
* **Протокол передачи данных**: MQTT (`paho-mqtt` v2.0+)
* **Брокер сообщений**: Публичный HiveMQ Broker (`broker.hivemq.com:1883`)
* **База данных**: SQLite3 (`database.py`)
* **Дашборд и визуализация**: Streamlit, Pandas
* **Алерты и уведомления**: `aiogram` 3.x, `python-dotenv`

---

## 📂 Структура проекта

```text
Iot_architecture_project/
├── publisher.py          # Эмулятор датчика, отправка по MQTT, вызов алертов и логирование
├── database.py           # Инициализация SQLite БД и CRUD-операции для журнала аномалий
├── dashboard.py          # Интерактивный Streamlit-дашборд (Живые метрики & Таблица из SQLite)
├── telegram_alerts.py    # Асинхронная отправка уведомлений через Telegram Bot API
├── .env.example          # Шаблон конфигурации переменных окружения
├── .gitignore            # Исключение виртуального окружения, БД и ключей из Git
└── requirements.txt      # Зависимости проекта
```

---

## 🚀 Быстрый запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/YOUR_USERNAME/Iot_architecture_project.git
cd Iot_architecture_project
```

### 2. Создание и активация виртуального окружения
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создай файл `.env` в корневой директории проекта на основе `.env.example`:

```bash
cp .env.example .env
```

Заполни `.env` своими данными от Telegram-бота:
```env
BOT_TOKEN=ваш_токен_бота_от_BotFather
CHAT_ID=ваш_telegram_chat_id
```

---

## 🖥️ Запуск системы

Для полноценной работы системы запусти **два отдельных терминала**:

### Терминал 1: Запуск эмулятора датчика
```bash
python publisher.py
```
*Генерирует показатели каждые 2 секунды. При выходе напряжения за границы `190V – 240V` записывает данные в `energy.db` и высылает алерт в Telegram.*

### Терминал 2: Запуск Streamlit-дашборда
```bash
streamlit run dashboard.py
```
*Перейди в браузере по адресу `http://localhost:8501` для просмотра показателей в реальном времени и истории аномалий.*

---

## 🛡️ Схема базы данных (Таблица `alerts`)

```sql
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    voltage REAL NOT NULL,
    current REAL NOT NULL,
    power REAL NOT NULL,
    alert_type TEXT NOT NULL
);
```

---

## 📄 Лицензия

Распространяется под лицензией MIT. Подробнее см. в файле `LICENSE`.