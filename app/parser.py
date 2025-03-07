from app.config import app
from app.tasks import FetchPageTask, ParseXmlTask
from celery import group
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="
    pages = [1, 2]  # Номера страниц для парсинга

    # Регистрация задач
    fetch_task = FetchPageTask()
    parse_task = ParseXmlTask()

    # Создаём группу задач для параллельного выполнения
    fetch_tasks = group(fetch_task.s(base_url + str(page)) for page in pages)
    fetch_results = fetch_tasks.apply_async().join()  # Запускаем и ждём завершения

    for links in fetch_results:
        if not links:
            logger.info("Ссылки не найдены. Пропуск страницы.")
            continue

        # Создаём группу задач для парсинга XML
        parse_tasks = group(parse_task.s(link) for link in links)
        parse_results = parse_tasks.apply_async().join()  # Запускаем и ждём завершения

        for print_form_url, publish_dt in zip(links, parse_results):
            # Выводим результат в формате "ссылка на печатную форму <print_form_url> - дата <publish_dt>"
            print(f'ссылка на печатную форму "{print_form_url}" - дата "{publish_dt}"')

if __name__ == "__main__":
    with app.connection():
        main()