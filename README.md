# Tender Parser

Этот проект парсит данные с сайта государственных закупок и использует Celery для асинхронного выполнения задач. Проект включает в себя:

- Парсинг тендеров с сайта госзакупок.
- Использование Celery для асинхронного выполнения задач.
- Docker-контейнеризацию для удобного развертывания.
- Тестирование в eager-режиме (синхронное выполнение задач).

## Содержание

1. [Зависимости](#зависимости)
2. [Установка](#установка)
3. [Запуск в PyCharm](#запуск-в-pycharm)
4. [Запуск с помощью Docker](#запуск-с-помощью-docker)
5. [Тестирование](#тестирование)
6. [Остановка](#остановка)
7. [Контакты](#контакты)

---

## Зависимости

Для работы проекта необходимы:

- Python 3.9
- Redis (для Celery)
- Docker (опционально, для контейнеризации)

---

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/ваш-репозиторий/tender_parser.git
   cd tender_parser
2. Создайте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate     # Windows
    ```
3. Активируйте виртуальное окружение:
    ```bash
    source venv/bin/activate  # Linux/MacOS
    ```
   ```bash
    venv\Scripts\activate     # Windows
    ```
4. Установите зависимости:
    ```bash
   pip install -r requirements.txt
   ```
5. Создайте файл ***.env*** в корне проекта на примере ***.env.sample***

## Запуск в PyCharm
1. Откройте проект в PyCharm.

2. Убедитесь, что виртуальное окружение активировано.

3. Запустите Redis локально (если не используете Docker):
   - **С использованием Docker**:
     Если у вас установлен Docker, выполните команду:
     ```bash
     docker run -d -p 6379:6379 redis
     ```

   - **Без Docker**:
     Если вы не хотите использовать Docker, установите Redis вручную:
     - **Linux** (например, Ubuntu):
       ```bash
       sudo apt update
       sudo apt install redis-server
       sudo systemctl start redis
       ```
     - **MacOS** (с использованием Homebrew):
       ```bash
       brew install redis
       brew services start redis
       ```
     - **Windows**:
       Скачайте Redis для Windows с [официального сайта](https://redis.io/download) и запустите его вручную.
4. Запустите Celery worker:

   ```bash
   celery -A app.config worker --loglevel=info
   ```
5. Запустите основной скрипт:
    ```bash
   python -m app.parser
   ```
## Запуск с помощью Docker
1. Соберите и запустите контейнеры:
    ```bash
   docker-compose up --build
   ```
2. Результаты парсинга будут выведены в консоль.

## Тестирование
#### Особенности тестирования:
Тесты выполняются в eager-режиме, что означает синхронное выполнение задач Celery.

В eager-режиме задачи выполняются сразу, без необходимости запуска отдельного Celery worker'а.
1. Для запуска тестов выполните:
    ```bash
   pytest tests/
   ```
   
## Остановка
1. Для остановки контейнеров выполните:
    ```bash
   docker-compose down
   ```

## Контакты
По всем вопросам обращайтесь:

Email: [talko.alexander@gmail.com](mailto:email)

Телефон: [+79991712335](tel:+7 999 171-23-35)

Telegram: [t.me/Alextalko](https://t.me/Alextalko)