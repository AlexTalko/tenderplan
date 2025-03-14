from app.config import app
from app.tasks import FetchPageTask
from celery import group
import logging
import time
import redis
import json
from dotenv import load_dotenv  # Импортируем load_dotenv
import os  # Импортируем os для работы с переменными окружения

# Загружаем переменные окружения из файла .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к Redis с использованием переменных из .env
redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=int(os.getenv('REDIS_DB'))
)


def main():
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="
    pages = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # Номера страниц для парсинга

    # Регистрация задачи
    fetch_task = FetchPageTask()

    # Создаём группу задач для параллельного выполнения поиска печатных форм
    fetch_tasks = group(fetch_task.s(base_url + str(page)) for page in pages)
    fetch_tasks.apply_async()  # Запускаем задачи параллельно

    try:
        # Ожидаем завершения задач и выводим промежуточные результаты
        while True:
            time.sleep(1)  # Проверяем результаты каждую секунду

            # Получаем все ключи из Redis
            keys = redis_client.keys('celery-task-meta-*')
            for key in keys:
                result = redis_client.get(key)
                if result:
                    try:
                        # Преобразуем строку в словарь с помощью json
                        result_data = json.loads(result.decode('utf-8'))
                        if result_data.get('status') == 'SUCCESS':
                            logger.info(result_data['result'])  # Выводим результат
                            redis_client.delete(key)  # Удаляем результат из Redis
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка декодирования JSON: {e}")
                    except Exception as e:
                        logger.error(f"Ошибка при обработке результата: {e}")

    except KeyboardInterrupt:
        logger.info("Парсер остановлен пользователем.")
    finally:
        logger.info("Завершение работы парсера.")


if __name__ == "__main__":
    logger.info("Запуск парсера")
    with app.connection():
        main()