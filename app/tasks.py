import logging
from datetime import datetime

import pytz
import requests
import xmltodict
from bs4 import BeautifulSoup
from celery import Task, chain, shared_task

# Настройка логгера
logger = logging.getLogger(__name__)


# Фильтр для исключения логов Celery
class NoCeleryFilter(logging.Filter):
    def filter(self, record):
        return not record.name.startswith("celery")


# Настраиваем логирование, чтобы отображались только нужные сообщения
logging.getLogger("celery").setLevel(logging.WARNING)  # Понижаем уровень логов Celery
logger.addFilter(NoCeleryFilter())  # Добавляем фильтр для исключения логов Celery

# Заголовки HTTP-запросов
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://zakupki.gov.ru/",
}


@shared_task
def print_result(publish_dt, print_form_url):
    """
    Callback-функция для вывода результата в консоль в формате: дата - ссылка.
    Форматирует дату в YYYY-MM-DD HH:MM:SS в московском часовом поясе (MSK, UTC+3).
    """
    try:
        # Парсим дату ISO и преобразуем в московский часовой пояс
        dt = datetime.fromisoformat(publish_dt.replace("Z", "+00:00"))
        msk_tz = pytz.timezone("Europe/Moscow")
        dt_msk = dt.astimezone(msk_tz)
        formatted_dt = dt_msk.strftime("%d-%m-%Y %H:%M:%S МСК")
        logger.info(f"{formatted_dt} - {print_form_url}")
        return f"{formatted_dt} - {print_form_url}"
    except ValueError as e:
        logger.error(f"Ошибка форматирования даты {publish_dt}: {e}")
        return f"{publish_dt} - {print_form_url}"  # Возвращаем исходную дату при ошибке


def find_publish_dt(data):
    """
    Рекурсивно ищет ключ 'publishDTInEIS' в словаре.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "publishDTInEIS":
                return value
            result = find_publish_dt(value)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_publish_dt(item)
            if result is not None:
                return result
    return None


class FetchPageTask(Task):
    name = "fetch_page_task"

    def run(self, page_url):
        try:
            session = requests.Session()
            response = session.get(page_url, headers=HEADERS)
            response.raise_for_status()

            # Парсим HTML и извлекаем ссылки на печатные формы тендеров
            soup = BeautifulSoup(response.text, "html.parser")
            links = []
            for a in soup.select(
                "a[href*='/epz/order/notice/ea20/view/common-info.html']"
            ):
                tender_url = "https://zakupki.gov.ru" + a["href"]
                print_form_url = tender_url.replace(
                    "/ea20/view/common-info.html", "/printForm/view.html"
                )
                links.append(print_form_url)

            # Для каждой ссылки создаём задачу на парсинг XML
            for link in links:
                chain(
                    ParseXmlTask().s(link),  # Задача парсинга XML
                    print_result.s(link),  # Callback-функция для вывода результата
                ).apply_async()

            return links
        except Exception as e:
            logger.error(f"Ошибка в fetch_page_task: {e}")
            self.retry(
                exc=e, countdown=10, max_retries=3
            )  # Повторная попытка в случае ошибки


class ParseXmlTask(Task):
    name = "parse_xml_task"

    def run(self, print_form_url):
        try:
            # Формируем URL для XML-формы
            xml_url = print_form_url.replace("view.html", "viewXml.html")

            session = requests.Session()
            response = session.get(xml_url, headers=HEADERS)

            if response.status_code == 404:
                logger.error(f"XML-форма не найдена: {xml_url}")
                return None

            response.raise_for_status()

            # Парсим XML в словарь
            xml_dict = xmltodict.parse(response.content)

            # Рекурсивно ищем ключ 'publishDTInEIS'
            publish_dt = find_publish_dt(xml_dict)

            if not publish_dt:
                logger.warning(f"Ключ publishDTInEIS не найден в XML: {xml_url}")

            return publish_dt
        except Exception as e:
            logger.error(f"Ошибка в parse_xml_task: {e}")
            self.retry(
                exc=e, countdown=10, max_retries=3
            )  # Повторная попытка в случае ошибки
