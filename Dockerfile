FROM python:3.11-slim

WORKDIR /app

COPY ./api/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./model/.gitkeep /app/model/.gitkeep
COPY ./config.json /app/config.json
COPY ./database /app/database
COPY ./preparation /app/preparation
COPY ./data_pipeline /app/data_pipeline
COPY ./utils /app/utils

ENV PYTHONPATH=/app
ENV ROOT_PATH=/app

COPY ./api/start.sh /app/start.sh
RUN chmod +x /app/start.sh