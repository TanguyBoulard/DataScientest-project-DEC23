FROM python:3.11-slim

WORKDIR /app

COPY ./config.json /app/config.json
COPY ./preparation /app/preparation
COPY ./data_pipeline /app/data_pipeline
COPY ./utils /app/utils
COPY ./database /app/database

RUN pip install python-dotenv pymongo sqlalchemy psycopg2-binary requests

ENV PYTHONPATH=/app

CMD ["python", "preparation/city_from_openweather.py"]