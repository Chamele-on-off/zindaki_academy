FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Важно: создаем необходимые директории
RUN mkdir -p /app/uploads /app/data

EXPOSE 7001

CMD ["gunicorn", "--bind", "0.0.0.0:7001", "--timeout", "120", "app:app"]