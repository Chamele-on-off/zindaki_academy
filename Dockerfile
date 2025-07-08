FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn  # Добавлен gunicorn

COPY . .

EXPOSE 7001

CMD ["gunicorn", "--bind", "0.0.0.0:7001", "app:app"]