# Dockerfile

FROM python:3.11-slim
WORKDIR /app

# install dependencies first (Docker caches this layer)

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy your code

COPY . .

# Cloud Run provides the port via $PORT (default 8080)

ENV PORT=8080

# start the FastAPI backend

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
