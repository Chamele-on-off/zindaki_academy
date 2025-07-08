FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Создаем папку для сертификатов
RUN mkdir -p /app/certs

EXPOSE 8000 8443

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--bind", "0.0.0.0:8443", \
     "--certfile", "${GUNICORN_CERTFILE}", "--keyfile", "${GUNICORN_KEYFILE}", \
     "--workers", "4", "app:app"]