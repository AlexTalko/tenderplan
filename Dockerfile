# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем bash
RUN apt-get update && apt-get install -y bash

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Создаем виртуальное окружение и устанавливаем зависимости
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Добавляем /app в PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Команда для запуска парсера
CMD ["bash", "-c", "source /opt/venv/bin/activate && python app/parser.py"]