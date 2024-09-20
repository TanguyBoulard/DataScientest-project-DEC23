#!/bin/bash

python /app/preparation/city_from_openweather.py
python /app/preparation/data_from_kaggle.py

if [ ! -f /app/model/model.joblib ]; then
    python /app/preparation/train_model.py
    timeout=500
    while [ ! -f /app/model/model.joblib ]; do
        sleep 30
        timeout=$((timeout - 10))
        if [ $timeout -le 0 ]; then
            exit 1
        fi
    done
fi

python /app/preparation/data_from_web_scrapping.py

if [ "$API_DEBUG" = "true" ]; then
    exec uvicorn api.app:app --host "$API_HOST" --port "$API_PORT" --reload
else
    exec uvicorn api.app:app --host "$API_HOST" --port "$API_PORT"
fi
