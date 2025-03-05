import celery
import requests
from bs4 import BeautifulSoup
import xmltodict

class FetchPageTask(celery.Task):
    name = "fetch_page_task"  # Уникальное имя задачи

    def run(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = soup.find_all('div', class_='search-registry-entry-block')
        links = []
        for tender in tenders:
            link = tender.find('a', class_='registry-entry__header-mid__number')['href']
            links.append(link)
        return links

class ParseXmlTask(celery.Task):
    name = "parse_xml_task"  # Уникальное имя задачи

    def run(self, url):
        response = requests.get(url)
        xml_data = xmltodict.parse(response.content)
        publish_dt = xml_data.get('root', {}).get('commonInfo', {}).get('publishDTInEIS', None)
        return publish_dt