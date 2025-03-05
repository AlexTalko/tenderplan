from .config import app


def main():
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber="
    pages = [1, 2]

    for page in pages:
        url = base_url + str(page)
        # Используем зарегистрированную задачу FetchPageTask
        links = app.send_task("fetch_page_task", args=[url]).get()

        for link in links:
            xml_url = link.replace('view.html', 'viewXml.html')
            # Используем зарегистрированную задачу ParseXmlTask
            publish_dt = app.send_task("parse_xml_task", args=[xml_url]).get()
            print(f"{link} - {publish_dt}")


if __name__ == "__main__":
    with app.connection():
        main()