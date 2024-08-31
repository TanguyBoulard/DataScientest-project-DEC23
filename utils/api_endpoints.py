import os
from typing import Dict
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}"
USERNAME = os.getenv('API_USER')
PASSWORD = os.getenv('API_PASSWORD')


def get_token(username: str, password: str) -> str:
    """
    Get a token from the API

    :param username: Username to authenticate with
    :param password: Password to authenticate with
    :return: token to use for authentication
    """
    response = requests.post(
        f"{BASE_URL}/token",
        data={'username': username, 'password': password}
    )
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get token: {response.status_code} - {response.text}")


def get_data(endpoint: str, token: str, params: Dict[str, str]) -> Dict:
    """
    Get data from the API

    :param endpoint: The endpoint to get data from
    :param token: The token to authenticate with
    :param params: The parameters to pass to the endpoint
    :return: The data from the endpoint
    """
    headers = {'Authorization': f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get data: {response.status_code} - {response.text}")


if __name__ == '__main__':
    token = get_token(USERNAME, PASSWORD)

    params = {'city': 'Canberra', 'date': '2024-9-5'}
    prediction = get_data('predict', token, params)
    print(prediction)
