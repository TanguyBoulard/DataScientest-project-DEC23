from datetime import datetime, timedelta

from airflow.operators.python import PythonOperator
from pendulum import timezone

from airflow import DAG
from data_pipeline.pipeline_manager import DataPipeline
from utils.ELTL import OpenWeatherCurrentWeather

pipeline = DataPipeline(OpenWeatherCurrentWeather())

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'timezone': 'Australia/Sydney',
    'start_date': datetime(2024, 12, 25, tzinfo=timezone('Australia/Sydney')),
    'catchup': False,
}


def scrape_weather_data_wrapper():
    from preparation.data_from_web_scrapping import scrap_weather_data, get_previous_month
    scrap_weather_data([get_previous_month()])


def retrain_model_wrapper():
    from preparation.train_model import train_model
    train_model()


def run_daily_weather_pipeline_wrapper():
    from data_pipeline.pipeline import run_daily_weather_pipeline
    run_daily_weather_pipeline()


def run_hour_weather_pipeline_wrapper():
    from data_pipeline.pipeline import run_hour_weather_pipeline
    run_hour_weather_pipeline()


def run_minutely_weather_pipeline_wrapper():
    from data_pipeline.pipeline import run_weather_pipeline
    run_weather_pipeline()


def extract_task():
    return pipeline.extract()


def load_to_datalake_task(ti):
    data = ti.xcom_pull(task_ids='extract')
    for data_dict in data:
        pipeline.load_to_datalake(data_dict)


def transform_task(ti):
    data = ti.xcom_pull(task_ids='extract')
    transformed_data = []
    for data_dict in data:
        transformed_data.append(pipeline.transform(data_dict))
    return transformed_data


def load_to_data_warehouse_task(ti):
    transformed_data = ti.xcom_pull(task_ids='transform')
    pipeline.load_to_data_warehouse(transformed_data)


# DAG for full weather data pipeline
with DAG(
    'full_weather_data_pipeline',
    default_args=default_args,
    description='Pipeline to extract, transform, and load weather data',
    schedule_interval='* * * * *',
) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_task,
    )

    load_to_datalake = PythonOperator(
        task_id='load_to_datalake',
        python_callable=load_to_datalake_task,
        provide_context=True,
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_task,
        provide_context=True,
    )

    load_to_data_warehouse = PythonOperator(
        task_id='load_to_data_warehouse',
        python_callable=load_to_data_warehouse_task,
        provide_context=True,
    )

    extract >> load_to_datalake >> transform >> load_to_data_warehouse


# DAG for monthly model retraining
with DAG(
        'monthly_model_retraining',
        default_args=default_args,
        description='A DAG to retrain the model',
        schedule_interval='0 0 1 * *',
) as dag_model_monthly:
    retrain_model_task = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model_wrapper,
    )

    retrain_model_task

# DAG for monthly web scraping
with DAG(
        'monthly_weather_scraping_and_model_retraining',
        default_args=default_args,
        description='A DAG to scrape weather data monthly and retrain the model',
        schedule_interval='0 0 1 * *',
) as dag_monthly:
    scrape_weather_data_task = PythonOperator(
        task_id='scrape_weather_data',
        python_callable=scrape_weather_data_wrapper,
    )

    retrain_model_task = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model_wrapper,
    )

    scrape_weather_data_task >> retrain_model_task

# DAG for hour pipeline runs
with DAG(
        'daily_weather_pipeline',
        default_args=default_args,
        description='A DAG to run the weather data pipeline daily',
        schedule_interval='0 0 * * *',
) as dag_daily:
    run_daily_weather_pipeline_task = PythonOperator(
        task_id='run_daily_weather_pipeline',
        python_callable=run_daily_weather_pipeline_wrapper,
    )

    run_daily_weather_pipeline_task

# DAG for hour pipeline runs
with DAG(
        'hour_weather_pipeline',
        default_args=default_args,
        description='A DAG to run the weather data pipeline hourly',
        schedule_interval='0 9,15 * * *',
) as dag_hourly:
    run_hour_weather_pipeline_task = PythonOperator(
        task_id='run_hour_weather_pipeline',
        python_callable=run_hour_weather_pipeline_wrapper,
    )

    run_hour_weather_pipeline_task

# DAG for minutely pipeline runs
with DAG(
        'minutely_weather_pipeline',
        default_args=default_args,
        description='A DAG to run the weather data pipeline minutely',
        schedule_interval='* * * * *',
) as dag_minutely:
    run_minutely_weather_pipeline_task = PythonOperator(
        task_id='run_minutely_weather_pipeline',
        python_callable=run_minutely_weather_pipeline_wrapper,
    )

    run_minutely_weather_pipeline_task
