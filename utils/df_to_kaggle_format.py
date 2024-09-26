import pandas as pd

from database.postgresql_functools import City


def transform_to_kaggle_format(df, postgres):
    df['date'] = pd.to_datetime(df['date'])
    df['city_id'] = df['location'].apply(
        lambda name: postgres.fetch_record(City, {'name': name}).id)

    daily_weather = df[['date', 'city_id', 'min_temp', 'max_temp', 'rainfall',
                        'evaporation', 'sunshine', 'wind_gust_dir', 'wind_gust_speed']]

    weather_9am = df.assign(date=lambda x: x['date'].apply(
        lambda date: f"{date.strftime('%Y-%m-%d')} 09:00:00")) \
        .rename(columns={'wind_dir_9am': 'wind_dir',
                         'wind_speed_9am': 'wind_speed',
                         'humidity_9am': 'humidity',
                         'pressure_9am': 'pressure',
                         'cloud_9am': 'cloud',
                         'temp_9am': 'temp'}) \
        [['date', 'city_id', 'wind_dir', 'wind_speed', 'humidity', 'pressure', 'cloud', 'temp']]

    weather_3pm = df.assign(date=lambda x: x['date'].apply(
        lambda date: f"{date.strftime('%Y-%m-%d')} 15:00:00")) \
        .rename(columns={'wind_dir_3pm': 'wind_dir',
                         'wind_speed_3pm': 'wind_speed',
                         'humidity_3pm': 'humidity',
                         'pressure_3pm': 'pressure',
                         'cloud_3pm': 'cloud',
                         'temp_3pm': 'temp'}) \
        [['date', 'city_id', 'wind_dir', 'wind_speed', 'humidity', 'pressure', 'cloud', 'temp']]

    return daily_weather, weather_9am, weather_3pm
