# DataScientest-project-DEC23

Repository for the final project of the DataScientest training program for cohort DEC23.

## Table of Contents

- [Project Overview](#project-overview)
- [Goals and Objectives](#goals-and-objectives)
- [Installation and Setup](#installation-and-setup)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Design Choices](#design-choices)
- [Known Issues](#known-issues)
- [Data Sources](#data-sources)
- [Machine Learning Model](#machine-learning-model)
- [API Endpoints](#api-endpoints)
- [Dashboard](#dashboard)
- [Project Layout](#project-layout)

## Project Overview

The Weather Prediction System is a comprehensive solution for collecting, storing, analyzing, and
predicting weather data for various locations in Australia. This system integrates data from
multiple sources, including web scraping, the OpenWeather API, and historical datasets, to provide
accurate weather information and predictions.

The project utilizes a microservices architecture, employing various technologies such as Docker,
FastAPI, MongoDB, PostgreSQL, Redis, Apache Airflow, and Dash to create a scalable and efficient
weather prediction platform.

## Goals and Objectives

1. Collect and integrate weather data from multiple sources.
2. Store and manage large volumes of weather data efficiently.
3. Provide daily weather information and predictions through an API.
4. Implement a machine learning model to predict the likelihood of rain for the next day.
5. Create a scalable and maintainable system architecture using modern technologies.
6. Develop an interactive dashboard for data visualization and analysis.

## Installation and Setup

1. Clone the repository.

2. Set up environment variables:
    - Copy the `example.env` file to `.env`
    - Fill in the necessary credentials and API keys in the `.env` file

3. Install Docker and Docker Compose if not already installed.

## Deployment

1. Build and start the containers:
    ```bash
    docker-compose up --build
    ```

2. Access the services (local deployment):
    - API: `http://localhost:8000`
    - Airflow: `http://localhost:8080`
    - Dash Dashboard: `http://localhost:8000/dashboard`

3. To stop the containers:
    ```bash
    docker-compose down
    ```
   
## Architecture

The system architecture consists of several components:

1. **Data Collection**:
    - Web scraping (Australian Bureau of Meteorology)
    - OpenWeather API
    - Historical data from Kaggle

2. **Data Storage**:
    - MongoDB (Data Lake): Stores raw, unprocessed data
    - PostgreSQL (Data Warehouse): Stores processed, structured data
    - Redis: Caches frequently accessed data and model predictions

3. **Data Processing**:
    - Apache Airflow: Orchestrates data collection and processing tasks

4. **Machine Learning**:
    - Scikit-learn: Implements the rain prediction model

5. **API and Dashboard**:
    - FastAPI: Provides RESTful API endpoints
    - Dash: Creates an interactive dashboard for data visualization

6. **Containerization and Orchestration**:
    - Docker: Containerizes the application and its dependencies
    - Docker Compose: Orchestrates multi-container deployment

## Design Choices

1. **Microservices Architecture**: Chosen for its scalability, maintainability, and flexibility.
   Each component (data collection, storage, processing, API, etc.) is implemented as a separate
   service, allowing for independent scaling and updates.

2. **Data Lake (MongoDB) and Data Warehouse (PostgreSQL)**: This dual-database approach allows for
   storing both raw, unstructured data (in MongoDB) and processed, structured data (in PostgreSQL).
   This separation provides flexibility in data processing and analysis workflows.

3. **Caching with Redis**: Implemented to improve performance by reducing database queries for
   frequently accessed data, such as weather predictions and API responses.

4. **Apache Airflow**: Selected for its robust scheduling and monitoring capabilities, making it
   ideal for orchestrating complex data collection and processing tasks.

5. **FastAPI**: Chosen for its high performance, automatic API documentation generation, and native
   support for asynchronous programming.

6. **Dash**: Used for creating an interactive dashboard, leveraging its ability to create complex
   visualizations with minimal code.

7. **Docker and Docker Compose**: Employed to ensure consistency across development and production
   environments, simplify deployment, and facilitate scaling.

8. **Machine Learning with Scikit-learn**: Utilized for its extensive collection of efficient tools
   for machine learning and statistical modeling, particularly suited for predictive data analysis.

## Known Issues

1. Deployment issue due to access denied error:
    - If you encounter access denied error during deployment, you may need to change the permissions
      of the `airflow/dags` and `airflow/logs` directories. Run the following commands:
       ```shell
       sudo chmod -R 777 airflow/dags/
       sudo chmod -R 777 airflow/logs/
       ```

2. Airflow retraining model issue:
    - If the Airflow task for retraining the model fails, you may need to change the permissions of
      the `model/` directory. Run the following command:
      ```shell
      sudo chmod -R 777 model/
      ```
3. The machine learning model is a simple proof-of-concept and may not provide accurate predictions
   in all cases.
4. The web scraping script may break if the structure of the website changes.
5. Any container issues:
   - Please run the following command:
      ```shell
      docker system prune -a --volumes
      ```

## Data Sources

1. **Australian Bureau of Meteorology**: Web scraped for current and historical weather data.
2. **OpenWeather API**: Used for real-time weather data and forecasts.
3. **Kaggle Dataset**: Historical weather data for model training and validation.

## Machine Learning Model

The system uses a Random Forest Classifier to predict the likelihood of rain for the next day. The
model is trained on historical weather data and uses features such as temperature, humidity,
pressure, and wind speed.

Model evaluation are performed in the `kaggle_study.ipynb` notebook.

## API Usage Guide

The Weather Prediction System API provides endpoints for accessing weather data and predictions.

### Base URL

When running locally, the base URL for the API is: `http://localhost:8000`

### Authentication

The API uses OAuth2 with JWT tokens for authentication. To access protected endpoints, you need to:

1. Obtain a token using the `/token` endpoint.
2. Include the token in the `Authorization` header of your requests.

### Endpoints

#### Health Check

**Endpoint:** `/health`

**Method:** `GET`

**Description:** Checks the health of the API and its dependencies.

**Response:**
   - `200 OK` if the service is healthy.
   - `503 Service Unavailable` if any dependency is down.

#### Login for Access Token

**Endpoint:** `/token`

**Method:** `POST`

**Description:** Authenticates a user and returns an access token.

**Request:**
   - `username`: The username of the user.
   - `password`: The password of the user.

**Response:**
   - `200 OK` with a JSON object containing the access token.
   - `401 Unauthorized` if the credentials are incorrect.

**Example:**
```bash
curl -X POST "http://localhost:8000/token" -d "username=user&password=pass"
```

#### Get Cities

**Endpoint:** `/cities`

**Method:** `GET`

**Description:** Retrieves a list of cities.

**Response:**
   - `200 OK` with a JSON array of cities.

**Example:**
```bash
curl -X GET "http://localhost:8000/cities"
```

#### Get Weather

**Endpoint:** `/weather`

**Method:** `GET`

**Description:** Retrieves weather data for a specified city and date range.

**Request Parameters:**
   - `city`: The name of the city.
   - `start_date`: The start date in `YYYY-MM-DD` format.
   - `end_date`: The end date in `YYYY-MM-DD` format.

**Response:**
   - `200 OK` with a JSON array of weather data.
   - `400 Bad Request` if the date format is incorrect or `start_date` is after `end_date`.
   - `404 Not Found` if no weather data is found for the specified city and date range.

**Example:**
```bash
curl -X GET "http://localhost:8000/weather?city=Sydney&start_date=2023-01-01&end_date=2023-01-07"
```

#### Predict Rain

**Endpoint:** `/predict`

**Method:** `GET`

**Description:** Predicts the likelihood of rain for a specified city and date.

**Request Parameters:**
   - `date`: The date in `YYYY-MM-DD` format.
   - `city`: The name of the city.

**Response:**
   - `200 OK` with a JSON object containing the prediction.
   - `400 Bad Request` if the date format is incorrect.
   - `404 Not Found` if no weather data is found for the specified city and date.
   - `401 Unauthorized` if the user is not authenticated.

**Example:**
```bash
curl -X GET "http://localhost:8000/predict?date=2023-01-01&city=Sydney" -H "Authorization: Bearer <your_token>"
```

## Dashboard

The Dash dashboard provides interactive visualizations of weather data and predictions. It includes:

- Historical weather trends
- Comparison of weather parameters across cities
- Rain prediction visualizations

Access the dashboard at `http://localhost:8000/dashboard`.

## Project Layout

The project is structured as follows:

```
.
├── airflow/
│   ├── dags/
│   │   └── main_dags.py
│   └── logs/
│       └── .gitkeep
├── api/
│   ├── init.py
│   ├── app.py
│   └── dash_app.py
├── data/
│   ├── csv/
│   │   ├── weather_study.csv
│   │   └── weatherAUS.csv
│   └── json/
│       ├── dataDailyAggregation.json
│       └── dataWeatherTimeStamp.json
├── data_pipeline/
│   ├── init.py
│   ├── pipeline.py
│   └── pipeline_manager.py
├── database/
│   └── init/
│       ├── init-mongo.js
│       ├── init-postgres.sh
│       └── init-postgres.sql
├── migrations/
│   ├── postgres-migration/
│   │   └── versions/
│   │       ├── env.py
│   │       ├── README.md
│   │       └── script.py.mako
│   ├── alembic.ini
│   ├── init.py
│   ├── mongodb_functools.py
│   ├── postgresql_functools.py
│   └── redis_functools.py
├── model/
│   └── .gitkeep
├── notebooks/
│   └── kaggle_study.ipynb
├── preparation/
│   ├── init.py
│   ├── air_pollution_from_openweather.py
│   ├── city_from_openweather.py
│   ├── data_from_kaggle.py
│   ├── data_from_Laurent.py
│   ├── data_from_web_scrapping.py
│   ├── data_to_csv.py
│   ├── train_model.py
│   └── weather_from_openweather.py
├── utils/
│   ├── init.py
│   ├── api_endpoints.py
│   ├── csv_functools.py
│   ├── df_to_kaggle_format.py
│   ├── ETLT.py
│   ├── json_functools.py
│   └── openweather_functools.py
├── venv/
├── .env
├── .gitignore
├── config.json
├── docker-compose.yml
├── Dockerfile
├── example.env
├── README.md
├── requirements.txt
└── start.sh
```