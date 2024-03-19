import os

import requests
import logging

from common.url_bulder import build_url
from common.util_file import write_data_to_csv

from dotenv import load_dotenv

from common.util_request import get_request

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


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
    url = get_open_weather_api(os.environ['OPEN_WEATHER_URL'] + '/data/2.5/weather', 44.34, 10.99)

    # Effectuer la requête POST
    result = get_request(url)

    if result is not None:
        print("Request successful. Result:", result)
        write_data_to_csv(output_csv_file, result['weather'])
    else:
        print("Failed to make POST request. Check logs for details.")
