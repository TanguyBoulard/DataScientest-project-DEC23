-- Create users if they don't exist
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${PG_USER}') THEN
    CREATE USER ${PG_USER} WITH ENCRYPTED PASSWORD '${PG_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${AIRFLOW_USER}') THEN
    CREATE USER ${AIRFLOW_USER} WITH ENCRYPTED PASSWORD '${AIRFLOW_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${AIRFLOW_ADMIN_USER}') THEN
    CREATE USER ${AIRFLOW_ADMIN_USER} WITH ENCRYPTED PASSWORD '${AIRFLOW_ADMIN_PASSWORD}' CREATEDB;
  END IF;
END
$$;

-- Create databases if they don't exist
SELECT 'CREATE DATABASE ${AIRFLOW_DB}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${AIRFLOW_DB}')
\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${AIRFLOW_DB} TO ${AIRFLOW_USER}, ${AIRFLOW_ADMIN_USER};
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${PG_USER};

-- Switch to main database
\c ${POSTGRES_DB}

-- Create tables (rest of your table creation code remains the same)
CREATE TABLE IF NOT EXISTS api_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS city (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    UNIQUE (latitude, longitude)
);

CREATE TABLE IF NOT EXISTS weather (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    temp FLOAT,
    sunrise TIME,
    sunset TIME,
    wind_dir VARCHAR(255),
    wind_speed FLOAT,
    cloud FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    city_id INTEGER NOT NULL REFERENCES city(id)
);

CREATE TABLE IF NOT EXISTS daily_weather (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    min_temp FLOAT,
    max_temp FLOAT,
    rainfall FLOAT,
    evaporation FLOAT,
    sunshine FLOAT,
    wind_gust_dir VARCHAR(255),
    wind_gust_speed FLOAT,
    city_id INTEGER NOT NULL REFERENCES city(id)
);

CREATE TABLE IF NOT EXISTS air_pollution (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    air_quality_index INTEGER,
    co_concentration FLOAT,
    no_concentration FLOAT,
    no2_concentration FLOAT,
    o3_concentration FLOAT,
    so2_concentration FLOAT,
    pm25_concentration FLOAT,
    pm10_concentration FLOAT,
    nh3_concentration FLOAT,
    city_id INTEGER NOT NULL REFERENCES city(id)
);

-- Insert initial users
INSERT INTO api_users (username, password)
VALUES ('${API_ADMIN_USER}', '${API_ADMIN_PASSWORD}'),
       ('${API_USER}', '${API_PASSWORD}')
ON CONFLICT (username) DO NOTHING;

-- Create view
CREATE OR REPLACE VIEW australian_meteorology_weather AS
SELECT
    dw.id,
    TO_CHAR(dw.date, 'YYYY-MM-DD') AS date,
    c.name AS location,
    dw.min_temp,
    dw.max_temp,
    dw.rainfall,
    dw.evaporation,
    dw.sunshine,
    dw.wind_gust_dir,
    dw.wind_gust_speed,
    w9.temp AS temp_9am,
    w9.humidity AS humidity_9am,
    w9.cloud AS cloud_9am,
    w9.wind_dir AS wind_dir_9am,
    w9.wind_speed AS wind_speed_9am,
    w9.pressure AS pressure_9am,
    w3.temp AS temp_3pm,
    w3.humidity AS humidity_3pm,
    w3.cloud AS cloud_3pm,
    w3.wind_dir AS wind_dir_3pm,
    w3.wind_speed AS wind_speed_3pm,
    w3.pressure AS pressure_3pm
FROM
    daily_weather dw
JOIN
    city c ON dw.city_id = c.id
LEFT JOIN
    weather w9 ON dw.city_id = w9.city_id
        AND DATE_TRUNC('day', w9.date) = DATE_TRUNC('day', dw.date)
        AND EXTRACT(HOUR FROM w9.date) = 9
LEFT JOIN
    weather w3 ON dw.city_id = w3.city_id
        AND DATE_TRUNC('day', w3.date) = DATE_TRUNC('day', dw.date)
        AND EXTRACT(HOUR FROM w3.date) = 15
ORDER BY
    location, date;

-- Grant privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${PG_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${PG_USER};

-- Switch to Airflow database
\c ${AIRFLOW_DB}

-- Grant privileges to Airflow user
GRANT ALL PRIVILEGES ON DATABASE ${AIRFLOW_DB} TO ${AIRFLOW_USER};
GRANT ALL PRIVILEGES ON SCHEMA public TO ${AIRFLOW_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${AIRFLOW_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${AIRFLOW_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO ${AIRFLOW_USER};