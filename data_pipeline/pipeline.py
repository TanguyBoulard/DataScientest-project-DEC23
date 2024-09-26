from data_pipeline.pipeline_manager import DataPipeline
from utils.ELTL import OpenWeatherCurrentAirPollution, OpenWeatherHourWeather, \
    OpenWeatherCurrentWeather, OpenWeatherDailyWeather


def run_air_pollution_pipeline():
    air_pollution_manager = DataPipeline(OpenWeatherCurrentAirPollution())
    air_pollution_manager.run()


def run_weather_pipeline():
    weather_manager = DataPipeline(OpenWeatherCurrentWeather())
    weather_manager.run()


def run_hour_weather_pipeline():
    weather_manager = DataPipeline(OpenWeatherHourWeather())
    weather_manager.run()


def run_daily_weather_pipeline():
    weather_manager = DataPipeline(OpenWeatherDailyWeather())
    weather_manager.run()


if __name__ == '__main__':
    run_weather_pipeline()
