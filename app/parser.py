from app.config import app
from app.tasks import FetchPageTask, ParseXmlTask
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="
    pages = [1, 2]  # Номера страниц для парсинга

    # Регистрация задач
    fetch_task = FetchPageTask()
    parse_task = ParseXmlTask()

    for page in pages:
        page_url = base_url + str(page)
        logger.info(f"Обработка страницы: {page_url}")

        # Получаем список ссылок на печатные формы тендеров
        links = fetch_task.apply(args=[page_url]).get()
        logger.info(f"Найдено ссылок: {len(links)}")

        if not links:
            logger.info("Ссылки не найдены. Пропуск страницы.")
            continue

        for print_form_url in links:
            # Получаем дату публикации из XML
            publish_dt = parse_task.apply(args=[print_form_url]).get()

            # Выводим результат в формате "ссылка на печатную форму" - "publishDTInEIS"
            print(f'"{print_form_url}" - "{publish_dt}"')

if __name__ == "__main__":
    with app.connection():
        main()