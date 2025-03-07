from app.config import app
from app.tasks import FetchPageTask, ParseXmlTask, print_result
from celery import group, chain
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="
    pages = [1, 2]  # Номера страниц для парсинга

    # Регистрация задач
    fetch_task = FetchPageTask()
    parse_task = ParseXmlTask()

    # Создаём группу задач для параллельного выполнения поиска печатных форм
    fetch_tasks = group(fetch_task.s(base_url + str(page)) for page in pages)
    fetch_results = fetch_tasks.apply_async().join()  # Запускаем и ждём завершения

    for links in fetch_results:
        if not links:
            logger.info("Ссылки не найдены. Пропуск страницы.")
            continue

        # Для каждой ссылки создаём цепочку задач: парсинг XML -> вывод результата
        for link in links:
            # Создаём цепочку задач: parse_task -> print_result
            chain(
                parse_task.s(link),  # Задача парсинга XML
                print_result.s(link)  # Callback-функция для вывода результата
            ).apply_async()

if __name__ == "__main__":
    logger.info("Запуск парсера")
    with app.connection():
        main()