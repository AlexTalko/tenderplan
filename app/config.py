from celery import Celery
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env
load_dotenv()

# Используем переменные окружения
broker_url = os.getenv("CELERY_BROKER_URL")  # Без значения по умолчанию
result_backend = os.getenv("CELERY_RESULT_BACKEND")  # Без значения по умолчанию

# Проверяем, что переменные окружения заданы
if not broker_url or not result_backend:
    raise ValueError("Не заданы переменные окружения CELERY_BROKER_URL и CELERY_RESULT_BACKEND")

app = Celery('tasks', broker=broker_url, backend=result_backend)

# Включаем eager-режим для тестирования
app.conf.update(
    task_always_eager=True,  # Задачи выполняются синхронно
    result_expires=3600,
)