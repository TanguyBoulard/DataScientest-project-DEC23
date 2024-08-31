import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, List, Union

from dotenv import load_dotenv

from database.mongodb_functools import MongoDBManager
from database.postgresql_functools import PostgresManager, Base, City, Weather, DailyWeather, \
    AirPollution
from utils.json_functools import load_from_json
from utils.openweather_functools import request_api, extract_lat_lon, build_date_timestamp, \
    deg_to_cardinal


class OpenWeatherAPI(ABC):
    root_path = Path(__file__).parents[1]

    load_dotenv(dotenv_path=root_path / '.env')
    api_key = os.getenv("OPENWEATHER_API_KEY")

    datalake_manager = MongoDBManager()
    data_warehouse_manager = PostgresManager()

    @abstractmethod
    def __init__(self):
        self.base_url: str = 'https://api.openweathermap.org/'
        self.endpoint: str = ''
        self.params: Dict[str, Optional[str, int]] = {
            'appid': self.api_key, 'lang': 'en'
        }
        self.collection_name: str = ''
        self.table_name = Base

    def url_builder(self) -> str:
        """
        Constructs a URL with given base URL, endpoint, and parameters.

        :return: The complete URL with parameters.
        """
        url = f"{self.base_url}{self.endpoint}?"
        param_str = "&".join(
            [f"{key}={value}" for key, value in self.params.items() if value is not None])
        return url + param_str

    @abstractmethod
    def extract_data(self) -> Union[Dict, List[Dict]]:
        """
        Fetches the raw data from the API.

        :return: The raw data fetched from the API.
        """

    @abstractmethod
    def transform_data(self, data: Dict) -> Union[Dict, List[Dict]]:
        """
        Structures the raw data into a format that can be loaded to the data warehouse.

        :param data: The raw data fetched from the API.
        :return: The structured data.
        """

    def load_to_datalake(self, data: Dict):
        """
        Loads the structured data to the MongoDB datalake.

        :param data: The structured data to be loaded.
        """
        self.datalake_manager.insert_document(self.collection_name, data)

    def load_to_data_warehouse(self, data: Dict):
        """
        Loads the structured data to the PostgresSQL data warehouse.

        :param data: The structured data to be loaded.
        """
        self.data_warehouse_manager.add_record(self.table_name(**data))


class OpenWeatherCity(OpenWeatherAPI):
    def __init__(self):
        super().__init__()

        config = load_from_json(os.path.join(self.root_path, 'config.json'))
        self.locations: List[str] = config['locations']
        self.country_code: str = config['country_code']

        self.endpoint = 'geo/1.0/direct'
        self.params['limit'] = '1'
        self.collection_name = 'city'
        self.table_name = City

    def extract_data(self) -> List[Dict]:
        data = []
        for city in self.locations:
            self.params['q'] = f"{city},{self.country_code}"
            data.append(request_api(self.url_builder())[0])
        return data

    def transform_data(self, data: Dict) -> Dict:
        return {
            'name': data['name'],
            'country': data['country'],
            'latitude': data['lat'],
            'longitude': data['lon']
        }


class OpenWeatherByCities(OpenWeatherAPI):
    def __init__(self):
        super().__init__()
        self.endpoint = 'data/'
        self.params['units'] = 'metric'

        cities_info = self.datalake_manager.find_documents('city', {})
        self.latitudes, self.longitudes = extract_lat_lon(cities_info)

    def extract_data(self) -> List[Dict]:
        data = []
        for lat, lon in zip(self.latitudes, self.longitudes):
            self.params['lat'] = lat
            self.params['lon'] = lon
            data.append(request_api(self.url_builder()))
        return data

    def get_city_id(self, latitude: float, longitude: float) -> int:
        """
        Fetches the city ID from the PostgreSQL database based on the
        provided latitude and longitude coordinates.

        :param latitude: The latitude of the location.
        :param longitude: The longitude of the location.
        :return: The city ID corresponding to the provided coordinates.
        """
        city_id = self.data_warehouse_manager.fetch_city_record_by_coord(latitude, longitude).id
        return city_id

    @abstractmethod
    def transform_data(self, data: Dict) -> Union[Dict, List[Dict]]:
        pass


class OpenWeatherCurrentWeather(OpenWeatherByCities):
    def __init__(self):
        super().__init__()
        self.endpoint = self.endpoint + '2.5/weather'
        self.collection_name = 'weather'
        self.table_name = Weather

    def transform_data(self, data: Dict) -> Dict:
        return {
                'date': build_date_timestamp(timestamp=data['dt'],
                                             timezone=data['timezone'],
                                             mode='datetime'),
                'temp': data['main']['temp'],
                'sunrise': build_date_timestamp(timestamp=data['sys']['sunrise'],
                                                timezone=data['timezone'],
                                                mode='hours'),
                'sunset': build_date_timestamp(timestamp=data['sys']['sunset'],
                                               timezone=data['timezone'],
                                               mode='hours'),
                'wind_dir': deg_to_cardinal(data['wind']['deg']),
                'wind_speed': data['wind']['speed'],
                'cloud': data['clouds']['all'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'city_id': self.get_city_id(data['coord']['lat'], data['coord']['lon'])
            }


class OpenWeatherDailyWeather(OpenWeatherByCities):
    def __init__(self, date: str):
        super().__init__()
        self.endpoint = self.endpoint + '3.0/onecall/day_summary'
        self.params['date'] = date
        self.collection_name = 'daily_weather'
        self.table_name = DailyWeather

    def transform_data(self, data: Dict) -> Dict:
        return {
            'date': data['date'],
            'min_temp': data['temperature']['min'],
            'max_temp': data['temperature']['max'],
            'rainfall': data['precipitation']['total'],
            'wind_gust_dir': deg_to_cardinal(data['wind']['max']['direction']),
            'wind_gust_speed': data['wind']['max']['speed'],
            'cloud': data['cloud_cover']['afternoon'],
            'humidity': data['humidity']['afternoon'],
            'pressure': data['pressure']['afternoon'],
            'city_id': self.get_city_id(data['lat'], data['lon'])
        }


class OpenWeatherTimestampWeather(OpenWeatherByCities):
    def __init__(self, timestamp: int):
        super().__init__()
        self.endpoint = self.endpoint + '3.0/onecall/timemachine'
        self.params['dt'] = timestamp
        self.collection_name = 'weather'
        self.table_name = Weather

    def transform_data(self, data: Dict) -> Dict:
        return {
            'date': build_date_timestamp(timestamp=data['data'][0]['dt'],
                                         timezone=data['timezone_offset'],
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
            'city_id': self.get_city_id(data['lat'], data['lon'])
        }


class OpenWeatherCurrentAirPollution(OpenWeatherByCities):
    def __init__(self):
        super().__init__()
        self.endpoint = self.endpoint + '2.5/air_pollution'
        self.collection_name = 'air_pollution'
        self.table_name = AirPollution

    def transform_data(self, data: Dict) -> Dict:
        return {
            'date': build_date_timestamp(data['list'][0]['dt'],
                                         mode='datetime'),
            'air_quality_index': data['list'][0]['main']['aqi'],
            'co_concentration': data['list'][0]['components']['co'],
            'no_concentration': data['list'][0]['components']['no'],
            'no2_concentration': data['list'][0]['components']['no2'],
            'o3_concentration': data['list'][0]['components']['o3'],
            'so2_concentration': data['list'][0]['components']['so2'],
            'pm25_concentration': data['list'][0]['components']['pm2_5'],
            'pm10_concentration': data['list'][0]['components']['pm10'],
            'nh3_concentration': data['list'][0]['components']['nh3'],
            'city_id': self.get_city_id(data['coord']['lat'], data['coord']['lon'])
        }


class OpenWeatherDailyAirPollution(OpenWeatherByCities):
    def __init__(self, start: int, end: int):
        super().__init__()
        self.endpoint = self.endpoint + '2.5/air_pollution/history'
        self.params['start'] = start
        self.params['end'] = end
        self.collection_name = 'air_pollution'
        self.table_name = AirPollution

    def transform_data(self, data: Dict) -> List[Dict]:
        structured_data = []
        for i in range(len(data['list'])):
            structured_data.append({
                'date': build_date_timestamp(data['list'][i]['dt'],
                                             mode='datetime'),
                'air_quality_index': data['list'][i]['main']['aqi'],
                'co_concentration': data['list'][i]['components']['co'],
                'no_concentration': data['list'][i]['components']['no'],
                'no2_concentration': data['list'][i]['components']['no2'],
                'o3_concentration': data['list'][i]['components']['o3'],
                'so2_concentration': data['list'][i]['components']['so2'],
                'pm25_concentration': data['list'][i]['components']['pm2_5'],
                'pm10_concentration': data['list'][i]['components']['pm10'],
                'nh3_concentration': data['list'][i]['components']['nh3'],
                'city_id': self.get_city_id(data['coord']['lat'], data['coord']['lon'])
            })
        return structured_data

    @staticmethod
    def transform_data_to_multiple_dicts(data):
        """
        Transforms the input data into a list of formatted dictionaries.
        :param data: A dictionary containing the data to be transformed.
        :return: A list of formatted dictionaries.
        """
        formatted_dicts = []

        for entry in data['list']:
            components = entry['components']
            main = entry['main']
            dt = entry['dt']

            formatted_dict = {
                'coord': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                },
                'list': [{
                    'components': {
                        'co': components['co'],
                        'nh3': components['nh3'],
                        'no': components['no'],
                        'no2': components['no2'],
                        'o3': components['o3'],
                        'pm10': components['pm10'],
                        'pm2_5': components['pm2_5'],
                        'so2': components['so2']
                    },
                    'dt': dt,
                    'main': {
                        'aqi': main['aqi']
                    }
                }]
            }

            formatted_dicts.append(formatted_dict)

        return formatted_dicts

    def load_to_datalake(self, data: Dict):
        """
        Loads the structured data to the MongoDB datalake.

        :param data: The structured data to be loaded.
        """
        formatted_datas = self.transform_data_to_multiple_dicts(data)
        for formatted_data in formatted_datas:
            self.datalake_manager.insert_document(self.collection_name, formatted_data)
