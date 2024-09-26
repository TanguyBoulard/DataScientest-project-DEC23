import unittest
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.api_endpoints import get_token, get_data


class TestWeatherPrediction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.base_url = f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}"
        cls.username = os.getenv('API_USER')
        cls.password = os.getenv('API_PASSWORD')

        cls.token = get_token(cls.base_url, cls.username, cls.password)

    def test_weather_prediction(self):
        city = 'Brisbane City'
        date = datetime.now().strftime('%Y-%m-%d')
        params = {
            'city': city,
            'date': date
        }

        result = get_data(self.base_url, 'predict', self.token, params)

        self.assertEqual(result['city'], city)
        self.assertEqual(result['date'], date)
        self.assertIn(result['rain_tomorrow'], ['yes', 'no'])

        expected_keys = ['city', 'date', 'rain_tomorrow']
        self.assertListEqual(list(result.keys()), expected_keys)


if __name__ == '__main__':
    unittest.main()