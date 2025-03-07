from app.config import app
from app.tasks import FetchPageTask
from celery import group
import logging
import time
import redis
import json  # Добавляем модуль json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def main():
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="
    pages = [1, 2]  # Номера страниц для парсинга

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
