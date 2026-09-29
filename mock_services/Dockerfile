FROM python:3.12-slim

WORKDIR /svc

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the service sources
COPY . .

# writable dirs for volumes (as root, BEFORE switching user)
RUN mkdir -p /data /mail

# run as non-root (the demo simulates a real banking/mail surface)
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /svc /data /mail
USER appuser

# bank_api.py is served by uvicorn on 8001, smtp_sink.py listens on 1025
# (actual commands are set per-service in docker-compose.yml)
EXPOSE 8001 1025