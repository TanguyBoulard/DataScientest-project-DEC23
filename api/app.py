from pathlib import Path
import os
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import base64

import joblib
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd
from starlette.responses import PlainTextResponse

from database.postgresql_functools import PostgresManager, City, APIUsers

load_dotenv()
root_path = Path().resolve().parent

SECRET_KEY = os.getenv('API_SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

postgres_manager = PostgresManager()

model_pipeline = joblib.load(os.path.join(root_path, 'model', 'random_forest_model.joblib'))

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
        postgres_manager.engine.connect()
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
async def get_cities(current_user: User = Depends(get_current_user)):
    return postgres_manager.fetch_table(City)


@app.get('/users')
async def get_users(current_user: User = Depends(get_current_user)):
    return postgres_manager.fetch_table(APIUsers)


@app.get('/predict')
async def predict_rain(date: str, city: str, current_user: User = Depends(get_current_user)):
    weather_data_df = pd.read_sql_query(
        'SELECT * '
        'FROM australian_meteorology_weather '
        f"WHERE location = '{city}' AND date = '{date}'",
        postgres_manager.engine) \
        .drop(columns=['id'])
    if weather_data_df.empty:
        raise HTTPException(status_code=404, detail='Data not found')

    weather_data_df['rain_today'] = 'Yes' if weather_data_df['rainfall'].iloc[0] >= 1 else 'No'
    prediction = model_pipeline.predict(weather_data_df)

    return {'city': city, 'date': date, 'rain tomorrow': prediction[0]}
