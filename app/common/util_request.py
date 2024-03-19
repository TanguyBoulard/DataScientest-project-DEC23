import requests
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_request(url):
    try:

        response = requests.get(url)

        if response.status_code == 200:
            result = response.json()
            return result
        else:
            logger.error(f"Failed to make POST request. Status code: {response.status_code}")
            return None
    except Exception as e:
        logger.exception(f"An error occurred while making the POST request : {e}")
        return None


