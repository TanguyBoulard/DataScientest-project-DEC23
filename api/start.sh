#!/bin/bash

python /app/preparation/city_from_openweather.py
python /app/preparation/data_from_web_scrapping.py
python /app/preparation/train_model.py

timeout=500
while [ ! -f /app/model/random_forest_model.joblib ]; do
    sleep 10
    timeout=$((timeout - 10))
    if [ $timeout -le 0 ]; then
        echo "Timeout reached: model is too long to run or error occurs."
        exit 1
    fi
done

if [ "$API_DEBUG" = "true" ]; then
    exec uvicorn app:app --host "$API_HOST" --port "$API_PORT" --reload
else
    exec uvicorn app:app --host "$API_HOST" --port "$API_PORT"
fi