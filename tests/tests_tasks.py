import pytest
from app.config import app
from app.tasks import FetchPageTask, ParseXmlTask

# Включаем eager-режим для тестов
app.conf.task_always_eager = True


def test_fetch_page_task():
    # Пример URL для тестирования
    url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=1"

    # Выполняем задачу
    result = FetchPageTask().run(url)

    # Проверяем, что результат не пустой
    assert isinstance(result, list)
    assert len(result) > 0


def test_parse_xml_task():
    # Пример XML-ссылки для тестирования
    xml_url = "https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338100004625000003"

    # Выполняем задачу
    result = ParseXmlTask().run(xml_url)

    # Проверяем, что результат либо строка, либо None
    assert result is None or isinstance(result, str)