import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from common.url_bulder import build_url
from common.util_request import get_request
from models.database import db

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

base_url = os.environ['OPEN_WEATHER_URL'] + '/data/2.5/weather'


def get_open_weather_api_by_city(base_url, city):
    try:
        params = {
            'q': city,

            'appid': os.environ['OPEN_WEATHER_KEY']
        }
        # Effectuer la requête GET à l'API OpenWeatherMap
        url = build_url(base_url, params, path="")
        response = get_request(url)

        clean_data = {i: response[i] for i in ["weather", "main"]}
        clean_data["weather"] = clean_data["weather"][0]
        return clean_data

    except Exception as e:
        # Si une exception se produit lors de la requête, imprimer l'erreur
        print("Une erreur s'est produite:", e)


def add_key(data, city):
    current = datetime.now().strftime("%H:%M:%S")
    data["time"] = current
    data["city"] = city

    return data


def add_data(db, cities):
    col = db["weather"]

    for city in cities:
        data = get_open_weather_api_by_city(base_url, city)
        data = add_key(data, city)
        col.insert_one(data)


def get_open_weather_api(base_url, lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': os.environ['OPEN_WEATHER_KEY']
    }

    return build_url(base_url, params, path="")


output_csv_file = "output.csv"
# Exemple d'utilisation
if __name__ == "__main__":
    # url = get_open_weather_api(os.environ['OPEN_WEATHER_URL'] + '/data/2.5/weather', 44.34, 10.99)

    add_data(db, ["courbevoie", "puteaux", "lourdes", "bourg-la-reine"])

    col = db["weather"]

    for i in list(col.find({"weather.main": "Clear"}, {"_id": 0, "city": 1})):
        print(i)

    print(
        col.count_documents(
            {
                "$and": [
                    {"main.temp_min": {"$gte": 285}},
                    {"main.temp_max": {"$lte": 291}},
                ]
            }
        )
    )

for i in list(col.aggregate([{"$group": {"_id": "$weather.main", "nb": {"$sum": 1}}}])):
    print(i)
