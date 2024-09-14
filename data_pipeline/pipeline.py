from data_pipeline.pipeline_manager import DataPipeline
from utils.ELTL import OpenWeatherCurrentAirPollution, OpenWeatherCurrentWeather


def run_air_pollution_pipeline():
    air_pollution_manager = DataPipeline(OpenWeatherCurrentAirPollution())
    air_pollution_manager.run()

def run_weather_pipeline():
    weather_manager = DataPipeline(OpenWeatherCurrentWeather())
    weather_manager.run()


if __name__ == '__main__':
    run_air_pollution_pipeline()
    run_weather_pipeline()
