FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./data/csv/weatherAUS.csv /app/data/csv/weatherAUS.csv
COPY ./config.json /app/config.json
COPY ./preparation /app/preparation
COPY ./data_pipeline /app/data_pipeline
COPY ./utils /app/utils

ENV PYTHONPATH=/app
ENV ROOT_PATH=/app

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh