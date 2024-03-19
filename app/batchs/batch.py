import os

import requests
import logging

from common.util_file import write_data_to_csv
from remote.openservice import get_open_weather_api
from remote.remote_service import get_request

url = get_open_weather_api(os.environ['OPEN_WEATHER_URL'] + '/data/2.5/weather', 44.34, 10.99)

# Effectuer la requête POST
result = get_request(url)

if result is not None:
    print("Request successful. Result:", result)
    write_data_to_csv('./cron.csv', result['weather'])
else:
    print("Failed to make POST request. Check logs for details.")

