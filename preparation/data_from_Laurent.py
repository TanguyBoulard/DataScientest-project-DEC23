import json
import os
from pathlib import Path

from dotenv import load_dotenv

from database.mongodb_functools import MongoDBManager
from database.postgresql_functools import PostgresManager, Weather, DailyWeather
from utils.openweather_functools import deg_to_cardinal, build_date_timestamp


def load_daily_weather(path, postgres, mongo):
    with open(os.path.join(path, 'data', 'json', 'dataDailyAggregation.json'), 'r') as f:
        for line in f:
            data = json.loads(line)

            mongo.insert_document('weather', data)

            city_id = postgres.fetch_city_record_by_coord(
                data['lat'],
                data['lon']).id

            weather = {'date': data['date'],
                       'min_temp': data['temperature']['min'],
                       'max_temp': data['temperature']['max'],
                       'rainfall': data['precipitation']['total'],
                       'wind_gust_dir': deg_to_cardinal(data['wind']['max']['direction']),
                       'wind_gust_speed': data['wind']['max']['speed'],
                       'city_id': city_id
                       }
            postgres.add_record(DailyWeather(**weather))


def load_timestamp_weather(path, postgres, mongo):
    with open(os.path.join(path, 'data', 'json', 'dataWeatherTimeStamp.json'), 'r') as f:
        for line in f:
            data = json.loads(line)

            mongo.insert_document('weather', data)

            city_id = postgres.fetch_city_record_by_coord(
                data['lat'],
                data['lon']).id

            weather = {'date': build_date_timestamp(timestamp=data['data'][0]['dt'],
                                                    timezone=3600,  # workaround
                                                    mode='datetime'),
                       'temp': data['data'][0]['temp'],
                       'sunrise': build_date_timestamp(timestamp=data['data'][0]['sunrise'],
                                                       timezone=data['timezone_offset'],
                                                       mode='hours'),
                       'sunset': build_date_timestamp(timestamp=data['data'][0]['sunset'],
                                                      timezone=data['timezone_offset'],
                                                      mode='hours'),
                       'wind_dir': deg_to_cardinal(data['data'][0]['wind_deg']),
                       'wind_speed': data['data'][0]['wind_speed'],
                       'cloud': data['data'][0]['clouds'],
                       'humidity': data['data'][0]['humidity'],
                       'pressure': data['data'][0]['pressure'],
                       'city_id': city_id
                       }
            postgres.add_record(Weather(**weather))


if __name__ == '__main__':
    dir_path = Path(__file__).parents[1]
    load_dotenv()
    mongo_manager = MongoDBManager()
    postgres_manager = PostgresManager()

    load_daily_weather(dir_path, postgres_manager, mongo_manager)
    load_timestamp_weather(dir_path, postgres_manager, mongo_manager)
