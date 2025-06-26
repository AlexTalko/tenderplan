from celery import Celery
from app.tasks import FetchPageTask, ParseXmlTask
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env
load_dotenv()

# Используем переменные окружения
broker_url = os.getenv("CELERY_BROKER_URL")
result_backend = os.getenv("CELERY_RESULT_BACKEND")

app = Celery('tasks', broker=broker_url, backend=result_backend)

# Регистрируем задачи
app.register_task(FetchPageTask())
app.register_task(ParseXmlTask())

app.conf.update(
    task_always_eager=True,  # Задачи выполняются синхронно при True
    result_expires=3600,
)