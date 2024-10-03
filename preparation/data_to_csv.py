import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from database.postgresql_functools import PostgresManager

if __name__ == '__main__':
    load_dotenv()
    postgres = PostgresManager()
    root_path = Path().resolve().parent

    df = pd.read_sql_table('australian_meteorology_weather', postgres.engine) \
        .drop(columns=['id'])
    df['rain_today'] = df['rainfall'].apply(lambda x: 'yes' if x >= 1 else 'no')
    df['rain_tomorrow'] = df['rain_today'].shift(-1).apply(lambda x: 'yes' if x == 'yes' else 'no')
    df.to_csv(os.path.join(root_path, 'data', 'csv', 'weather_study.csv'), index=False)
