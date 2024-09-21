import base64
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.responses import PlainTextResponse

from api.dash_app import dash_app
from database.mongodb_functools import MongoDBManager
from database.postgresql_functools import PostgresManager, City, APIUsers
from database.redis_functools import RedisManager

load_dotenv()
root_path = os.getenv('ROOT_PATH')

SECRET_KEY = os.getenv('API_SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

postgres_manager = PostgresManager()
mongo_manager = MongoDBManager()
redis_manager = RedisManager()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    username: str
    hashed_password: Optional[str] = None


def verify_password(plain_password, hashed_password):
    hashed, salt = hashed_password.split(':')
    password_to_check = hashlib.sha512((plain_password + salt).encode('utf-8')).digest()
    password_to_check = base64.b64encode(password_to_check).decode('utf-8')
    return password_to_check == hashed


def get_user(username: str) -> Optional[User]:
    user = postgres_manager.fetch_record(APIUsers, {'username': username})
    if user:
        return User(username=user.username, hashed_password=user.password)
    return None


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        user = get_user(username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


@app.get('/health', response_class=PlainTextResponse)
async def health_check():
    try:
        # Check database connection
        assert postgres_manager.health_check()
        assert mongo_manager.health_check()
        assert redis_manager.health_check()
        return 'OK'
    except Exception:
        raise HTTPException(status_code=503, detail='Service Unavailable')


@app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


@app.get('/cities')
async def get_cities():
    # Try to get cities from Redis cache
    cities_cache = redis_manager.get('all_cities')

    if cities_cache:
        return cities_cache

    # If not in cache, fetch from database
    cities = postgres_manager.fetch_table(City)
    cities_data = [{'name': city.name, 'id': city.id} for city in cities]

    # Cache the result in Redis
    redis_manager.set('all_cities', cities_data, expiration=86400)

    return cities_data


@app.get('/weather')
async def get_weather(city: str, start_date: str, end_date: str):
    try:
        # Validate dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        if start > end:
            raise ValueError('start_date must be before or equal to end_date')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate cache key
    cache_key = f"weather:{city}:{start_date}:{end_date}"

    # Try to get weather data from Redis cache
    cached_weather = redis_manager.get(cache_key)

    if cached_weather:
        return cached_weather

    # If not in cache, fetch from database
    results = postgres_manager.fetch_weather_data(city, start_date, end_date)
    weather_data = [{
        'date': row.date,
        'max_temp': row.max_temp,
        'min_temp': row.min_temp,
        'rainfall': row.rainfall,
        'humidity_9am': row.humidity_9am,
        'humidity_3pm': row.humidity_3pm
    } for row in results]

    if not weather_data:
        raise HTTPException(status_code=404,
                            detail=f"No weather data found for {city} between {start_date} and {end_date}")

    # Cache the result in Redis
    redis_manager.set(cache_key, weather_data, expiration=3600)

    return weather_data


@app.get('/predict')
async def predict_rain(date: str, city: str, current_user: User = Depends(get_current_user)):
    try:
        # Validate date and get previous day
        try:
            prediction_date = datetime.strptime(date, '%Y-%m-%d')
            previous_day = (prediction_date - timedelta(days=1)).strftime('%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid date format. Use YYYY-MM-DD.')

        # Check if city exists
        if not postgres_manager.fetch_record(City, {'name': city}):
            raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

        # Try to get weather data from cache
        cache_key = f"weather_data:{city}:{previous_day}"
        weather_data = redis_manager.get(cache_key)

        if not weather_data:
            # If not in cache, fetch from database
            result = postgres_manager.fetch_weather_data_for_city_and_date(city, previous_day)
            weather_data_df = pd.DataFrame(
                [{c.name: getattr(obj, c.name) for c in obj.__table__.columns} for obj in result])
            if weather_data_df.empty:
                raise HTTPException(status_code=404,
                                    detail=f"No weather data found for {city} on {previous_day}.")

            weather_data = weather_data_df.to_dict('records')[0]
            redis_manager.set(cache_key, weather_data, expiration=3600)

        # Prepare data for prediction
        weather_data['rain_today'] = 'yes' if weather_data.get('rainfall', 0) >= 1 else 'no'
        prediction_data = pd.DataFrame([weather_data])

        # Get model and label encoder from cache or load from file
        model = redis_manager.get_serializable_object('weather_prediction_model')
        target_label_encoder = redis_manager.get_serializable_object('weather_label_encoder')

        if model is None or target_label_encoder is None:
            model_path = os.path.join(root_path, 'model', 'weather_model.joblib')
            label_encoder_path = os.path.join(root_path, 'model', 'label_encoder.joblib')
            try:
                if model is None:
                    model = joblib.load(model_path)
                    redis_manager.set_serializable_object('weather_prediction_model', model,
                                                          expiration=86400)
                if target_label_encoder is None:
                    target_label_encoder = joblib.load(label_encoder_path)
                    redis_manager.set_serializable_object('weather_label_encoder',
                                                          target_label_encoder, expiration=86400)
            except FileNotFoundError:
                raise HTTPException(status_code=500,
                                    detail='Model or label encoder file not found. Please ensure the model is trained.')

        # Make prediction
        prediction = model.predict(prediction_data)

        # Decode prediction
        decoded_prediction = target_label_encoder.inverse_transform(prediction)[0]

        return {
            'city': city,
            'date': date,
            'rain_tomorrow': decoded_prediction
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'An unexpected error occurred: {str(e)}')


app.mount('/dashboard', WSGIMiddleware(dash_app.server))
