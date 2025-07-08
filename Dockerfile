FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN mkdir -p /app/uploads /app/data /app/certs

EXPOSE 8000 8443

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 --bind 0.0.0.0:8443 \
     --certfile /app/certs/fullchain.pem \
     --keyfile /app/certs/privkey.pem \
     --workers 4 app:app"]
