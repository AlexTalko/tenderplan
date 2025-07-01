import logging
import os

import redis
from celery import group
from dotenv import load_dotenv

from app.config import app
from app.tasks import FetchPageTask

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Подключение к Redis
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB")),
)


def get_pages_from_user():
    """
    Запрашивает у пользователя диапазон или список страниц для парсинга.
    Возвращает список номеров страниц.
    """
    while True:
        mode = input(
            "Выберите режим ввода страниц (1 - диапазон, 2 - список номеров): "
        ).strip()
        if mode not in ["1", "2"]:
            logger.error("Некорректный выбор режима. Введите 1 или 2.")
            continue

        if mode == "1":
            # Ввод диапазона страниц (например, 1-10)
            range_input = input("Введите диапазон страниц (например, 1-10): ").strip()
            try:
                start, end = map(int, range_input.split("-"))
                if start <= 0 or end < start:
                    logger.error(
                        "Начальная страница должна быть положительной и меньше или равна конечной."
                    )
                    continue
                return list(range(start, end + 1))
            except ValueError:
                logger.error(
                    "Некорректный формат диапазона. Введите в формате 'начало-конец', например, 1-10."
                )
                continue

        else:
            # Ввод списка страниц (например, 1,3,5)
            pages_input = input(
                "Введите номера страниц через запятую (например, 1,3,5): "
            ).strip()
            try:
                pages = [int(page.strip()) for page in pages_input.split(",")]
                if not pages or any(page <= 0 for page in pages):
                    logger.error(
                        "Все номера страниц должны быть положительными числами."
                    )
                    continue
                return pages
            except ValueError:
                logger.error(
                    "Некорректный формат списка. Введите номера страниц через запятую, например, 1,3,5."
                )
                continue


def main():
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="

    # Запрашиваем страницы у пользователя
    pages = get_pages_from_user()
    logger.info(f"Выбраны страницы для парсинга: {pages}")

    # Регистрация задачи
    fetch_task = FetchPageTask()

    try:
        # Создаём группу задач
        fetch_tasks = group(fetch_task.s(base_url + str(page)) for page in pages)
        result = fetch_tasks.apply_async(
            expires=300
        )  # Запускаем задачи с таймаутом 5 минут

        # Ожидаем завершения всех задач
        for task in result:
            try:
                task.wait(timeout=300)  # Таймаут на задачу
                if not task.successful():
                    logger.error(
                        f"Задача {task.id} завершилась с ошибкой: {task.get(propagate=False)}"
                    )
            except Exception as e:
                logger.error(f"Ошибка при ожидании задачи {task.id}: {e}")

    except redis.RedisError as e:
        logger.error(f"Ошибка подключения к Redis: {e}")
    except KeyboardInterrupt:
        logger.info("Парсер остановлен пользователем.")
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
    finally:
        logger.info("Завершение работы парсера.")


if __name__ == "__main__":
    logger.info("Запуск парсера")
    with app.connection():
        main()
