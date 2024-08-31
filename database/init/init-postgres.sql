CREATE USER ${PG_USER} WITH ENCRYPTED PASSWORD '${PG_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${PG_USER};

\connect ${POSTGRES_DB};

CREATE TABLE api_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO api_users (
    username,
    password
) VALUES
    ('${API_ADMIN_USER}', '${API_ADMIN_PASSWORD}'),
    ('${API_USER}', '${API_PASSWORD}');

CREATE TABLE city (
    id SERIAL PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    country   VARCHAR(255),
    latitude  FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

CREATE TABLE weather (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    temp FLOAT,
    sunrise TIME,
    sunset TIME,
    wind_dir VARCHAR(255),
    wind_speed FLOAT,
    cloud    FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    city_id INTEGER NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(id)
);

CREATE TABLE daily_weather (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    min_temp FLOAT,
    max_temp FLOAT,
    rainfall FLOAT,
    evaporation FLOAT,
    sunshine FLOAT,
    wind_gust_dir VARCHAR(255),
    wind_gust_speed FLOAT,
    city_id INTEGER NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(id)
);

CREATE TABLE air_pollution (
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
    city_id INTEGER NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(id)
);

CREATE VIEW australian_meteorology_weather AS
    SELECT
        dw.id,
        EXTRACT(YEAR FROM dw.date) || '-' || EXTRACT(MONTH FROM dw.date) || '-' || EXTRACT(DAY FROM dw.date) AS date,
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
                          AND EXTRACT(HOUR FROM w9.date) = 9
                          AND EXTRACT(YEAR FROM dw.date) = EXTRACT(YEAR FROM w9.date)
                          AND EXTRACT(MONTH FROM dw.date) = EXTRACT(MONTH FROM w9.date)
                          AND EXTRACT(DAY FROM dw.date) = EXTRACT(DAY FROM w9.date)
    LEFT JOIN
        weather w3 ON dw.city_id = w3.city_id
                          AND EXTRACT(HOUR FROM w3.date) = 15
                          AND EXTRACT(YEAR FROM dw.date) = EXTRACT(YEAR FROM w3.date)
                          AND EXTRACT(MONTH FROM dw.date) = EXTRACT(MONTH FROM w3.date)
                          AND EXTRACT(DAY FROM dw.date) = EXTRACT(DAY FROM w3.date)
    ORDER BY
        location, date;


GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${PG_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${PG_USER};