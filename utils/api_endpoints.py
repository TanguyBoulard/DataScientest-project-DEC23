import os
from datetime import datetime
from typing import Dict

import requests
from dotenv import load_dotenv


def get_token(base_url: str, username: str, password: str) -> str:
    """
    Get a token from the API

    :param base_url: The base URL of the API
    :param username: Username to authenticate with
    :param password: Password to authenticate with
    :return: token to use for authentication
    """
    response = requests.post(
        f"{base_url}/token",
        data={'username': username, 'password': password}
    )
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get token: {response.status_code} - {response.text}")


def get_data(base_url: str, endpoint: str, token: str, params: Dict[str, str]) -> Dict:
    """
    Get data from the API

    :param base_url: The base URL of the API
    :param endpoint: The endpoint to get data from
    :param token: The token to authenticate with
    :param params: The parameters to pass to the endpoint
    :return: The data from the endpoint
    """
    headers = {'Authorization': f"Bearer {token}"}

    response = requests.get(f"{base_url}/{endpoint}", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get data: {response.status_code} - {response.text}")


if __name__ == '__main__':
    load_dotenv()
    base_url = f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}"
    username = os.getenv('API_USER')
    password = os.getenv('API_PASSWORD')

    token = get_token(base_url, username, password)

    today = (datetime.now()).strftime('%Y-%m-%d')
    params = {'city': 'Brisbane City', 'date': today}
    prediction = get_data(base_url, 'predict', token, params)
