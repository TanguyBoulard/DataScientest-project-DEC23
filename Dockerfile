FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./config.json /app/config.json
COPY ./database /app/database
COPY ./preparation /app/preparation
COPY ./data_pipeline /app/data_pipeline
COPY ./utils /app/utils

ENV PYTHONPATH=/app
ENV ROOT_PATH=/app

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh