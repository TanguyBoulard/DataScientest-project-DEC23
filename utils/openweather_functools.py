"""
This module contains utility functions for fetching and processing data
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import requests


def request_api(url: str) -> Dict:
    """
    Requests data from the specified URL and returns the response as a dictionary.
    Raises an exception for non-200 responses.

    :param url: The URL from which to fetch the data.
    :return: The data retrieved from the API, parsed into a dictionary.
    :raises ConnectionError: If the API response status code is not 200.
    """
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data
    raise ConnectionError(f"Web server response: {response.status_code}")


def extract_lat_lon(data: List[Dict]) -> Tuple[List[float], List[float]]:
    """
    Extracts latitudes and longitudes for locations within
    the specified country from the provided dataset.

    :param data: A list of dictionaries, each representing a location.
    :return: A tuple containing two lists:
        * The first list contains the latitudes of locations within the specified country.
        * The second list contains the longitudes of these locations.
    """
    latitudes, longitudes = [], []
    for location in data:
        latitudes.append(location['lat'])
        longitudes.append(location['lon'])
    return latitudes, longitudes


def build_date_timestamp(timestamp: int, timezone: int = 0, mode: str = 'date') -> str:
    """
    Converts a UNIX timestamp to a formatted date or
    time string based on timezone and mode.
    :param timestamp: UNIX timestamp.
    :param timezone: Timezone offset in seconds.
    :param mode: 'date' for date string, 'hours' for time string.
    :return: Formatted date or time string.
    :raise: NotImplementedError if mode is not 'date' or 'hours'.
    """
    # Convert timestamp to UTC datetime
    utc_time = datetime.utcfromtimestamp(timestamp)
    # Create timedelta object for timezone offset
    timezone_offset = timedelta(seconds=timezone)
    # Apply timezone offset to UTC time
    local_time = utc_time + timezone_offset

    # Return formatted date or time based on mode
    if mode == 'date':
        return local_time.strftime('%Y-%m-%d')
    elif mode == 'hours':
        return local_time.strftime('%H:%M:%S')
    elif mode == 'datehours':
        return local_time.strftime('%Y-%m-%d %H:00:00')
    elif mode == 'datetime':
        return local_time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise NotImplementedError


def deg_to_cardinal(deg: float) -> str:
    """
    Converts a degree to its corresponding cardinal direction.
    :param deg: Degree to be converted.
    :return: A string representing the cardinal direction.
    """
    directions = [
        'N', 'NNE', 'NE', 'ENE',
        'E', 'ESE', 'SE', 'SSE',
        'S', 'SSW', 'SW', 'WSW',
        'W', 'WNW', 'NW', 'NNW', 'N'
    ]
    # Calculate index for the directions list
    index = int((deg + 11.25) % 360 / 22.5)
    return directions[index]


def get_rain_info(data: Optional[Dict[str, Dict[str, float]]] = None) -> float:
    """
    Extracts 1-hour rain volume information from data, if available.
    :param data: Optional dictionary containing weather data,
        including rain information structured as {'rain': {'1h': float}}.
        Defaults to None.
    :return: The volume of rain in the last 1-hour in millimeters.
        Returns 0.0 if data is unavailable or does not contain the
        required information.
    """
    # Check if data is None and initialize it to a default value if so
    if data is None:
        data = {'rain': {'1h': 0.0}}
    # Safely extract and return the rain volume, defaulting to 0.0 if not present
    return float(data.get('rain', {}).get('1h', 0.0))
