from datetime import datetime

import pandas as pd

from data_pipeline.pipeline_manager import DataPipeline
from utils.ELTL import OpenWeatherTimestampWeather, OpenWeatherDailyWeather


def generate_timestamps(date):
    dt_9am = datetime(date.year, date.month, date.day, 9, 0)
    dt_3pm = datetime(date.year, date.month, date.day, 15, 0)

    timestamp_9am = int(dt_9am.timestamp())
    timestamp_3pm = int(dt_3pm.timestamp())

    return timestamp_9am, timestamp_3pm


if __name__ == '__main__':
    start_date = '2017-01-01'
    end_date = '2024-01-01'

    dates = pd.date_range(start_date, end_date, freq='D')

    for date in dates:
        timestamp_9am, timestamp_3pm = generate_timestamps(date)

        daily_Weather_manager = DataPipeline(OpenWeatherDailyWeather(
            date=date.strftime("%Y-%m-%d")))
        daily_Weather_manager.run()

        timestamp_Weather_manager = DataPipeline(OpenWeatherTimestampWeather(
            timestamp=timestamp_9am))
        timestamp_Weather_manager.run()

        timestamp_Weather_manager = DataPipeline(OpenWeatherTimestampWeather(
            timestamp=timestamp_3pm))
        timestamp_Weather_manager.run()
