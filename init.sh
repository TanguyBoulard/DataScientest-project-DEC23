#!/bin/bash

python /app/preparation/city_from_openweather.py
python /app/preparation/data_from_kaggle.py

if [ ! -f /app/model/weather_prediction_model.joblib ] || [ ! -f /app/model/weather_label_encoder.joblib ]; then
  python /app/preparation/train_model.py
  timeout=300
  while [ ! -f /app/model/weather_prediction_model.joblib ] || [ ! -f /app/model/weather_label_encoder.joblib ]; do
      sleep 10
      timeout=$((timeout - 10))
      if [ $timeout -le 0 ]; then
          exit 1
      fi
  done
fi

python /app/preparation/data_from_web_scrapping.py
