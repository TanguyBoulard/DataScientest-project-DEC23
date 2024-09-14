from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pendulum import timezone
import pendulum

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def get_previous_month():
    today = pendulum.now(timezone('Australia/Sydney'))
    first_of_month = today.replace(day=1)
    last_month = first_of_month.subtract(days=1)
    return last_month.format('YYYYMM')

def scrape_weather_data_wrapper():
    from preparation.data_from_web_scrapping import scrap_weather_data
    dates_to_scrape = [get_previous_month()]
    scrap_weather_data(dates_to_scrape)

def run_air_pollution_pipeline_wrapper():
    from data_pipeline.pipeline import run_air_pollution_pipeline
    run_air_pollution_pipeline()

def run_weather_pipeline_wrapper():
    from data_pipeline.pipeline import run_weather_pipeline
    run_weather_pipeline()

# DAG for monthly web scraping
with DAG(
    'monthly_weather_scraping',
    default_args=default_args,
    description='A DAG to scrape weather data monthly',
    schedule_interval='0 0 1 * *',
    start_date=datetime(2024, 9, 20),
    catchup=False,
) as dag_monthly:
    scrape_weather_data_task = PythonOperator(
        task_id='scrape_weather_data',
        python_callable=scrape_weather_data_wrapper,
    )

# DAG for daily pipeline runs
with DAG(
    'daily_weather_pipeline',
    default_args=default_args,
    description='A DAG to run the weather data pipeline daily',
    schedule_interval='0 9,15 * * *',
    start_date=datetime(2024, 9, 20, tzinfo=timezone('Australia/Sydney')),
    catchup=False,
) as dag_daily:

    run_weather_pipeline_task = PythonOperator(
        task_id='run_weather_pipeline',
        python_callable=run_weather_pipeline_wrapper,
    )

    run_weather_pipeline_task
