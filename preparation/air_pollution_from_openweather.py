from datetime import datetime

from data_pipeline.pipeline_manager import DataPipeline
from utils.ELTL import OpenWeatherDailyAirPollution


def date_to_timestamp(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d") \
        .replace(hour=0)

    timestamp = int(dt.timestamp())
    return timestamp


if __name__ == '__main__':
    start_date = '2020-01-01'
    end_date = '2024-01-01'

    daily_air_pollution_manager = DataPipeline(OpenWeatherDailyAirPollution(
        start=date_to_timestamp(start_date), end=date_to_timestamp(end_date)))
    daily_air_pollution_manager.run()
