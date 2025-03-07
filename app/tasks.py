from celery import Task
import requests
from bs4 import BeautifulSoup
import xmltodict
import logging

logger = logging.getLogger(__name__)

class FetchPageTask(Task):
    name = "fetch_page_task"

    def run(self, page_url):
        try:
            logger.info(f"Запуск задачи fetch_page_task для URL: {page_url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://zakupki.gov.ru/",
            }
            session = requests.Session()
            response = session.get(page_url, headers=headers)
            response.raise_for_status()

            # Парсим HTML и извлекаем ссылки на печатные формы тендеров
            soup = BeautifulSoup(response.text, "html.parser")
            links = []
            for a in soup.select("a[href*='/epz/order/notice/ea20/view/common-info.html']"):
                tender_url = "https://zakupki.gov.ru" + a["href"]
                # Исправляем формирование URL для печатной формы
                print_form_url = tender_url.replace("/ea20/view/common-info.html", "/printForm/view.html")
                links.append(print_form_url)

            logger.info(f"Найдено ссылок: {len(links)}")
            return links
        except Exception as e:
            logger.error(f"Ошибка в fetch_page_task: {e}")
            self.retry(exc=e)  # Повторная попытка в случае ошибки


class ParseXmlTask(Task):
    name = "parse_xml_task"

    def run(self, print_form_url):
        try:
            logger.info(f"Запуск задачи parse_xml_task для URL: {print_form_url}")
            # Формируем URL для XML-формы
            xml_url = print_form_url.replace("view.html", "viewXml.html")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://zakupki.gov.ru/",
            }
            session = requests.Session()
            response = session.get(xml_url, headers=headers)

            if response.status_code == 404:
                logger.error(f"XML-форма не найдена: {xml_url}")
                return None

            response.raise_for_status()

            # Парсим XML и извлекаем дату публикации
            xml_dict = xmltodict.parse(response.content)
            publish_dt = xml_dict.get("ns2:notice", {}).get("commonInfo", {}).get("publishDTInEIS")
            return publish_dt
        except Exception as e:
            logger.error(f"Ошибка в parse_xml_task: {e}")
            self.retry(exc=e)  # Повторная попытка в случае ошибки