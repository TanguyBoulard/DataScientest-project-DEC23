#!/bin/bash

if [ ! -d /app/database/postgres_data ] || [ ! -d /app/database/mongo_data ]; then
  python /app/preparation/city_from_openweather.py
  python /app/preparation/data_from_kaggle.py
fi

if [ ! -f /app/model/random_forest_model.joblib ]; then
  python /app/preparation/train_model.py

    timeout=300
    while [ ! -f /app/model/random_forest_model.joblib ]; do
        sleep 10
        timeout=$((timeout - 10))
        if [ $timeout -le 0 ]; then
            exit 1
        fi
    done
fi

if [ ! -d /app/database/postgres_data ] || [ ! -d /app/database/mongo_data ]; then
  python /app/preparation/data_from_web_scrapping.py
fi

if [ "$API_DEBUG" = "true" ]; then
    exec uvicorn app:app --host "$API_HOST" --port "$API_PORT" --reload
else
    exec uvicorn app:app --host "$API_HOST" --port "$API_PORT"
fi
