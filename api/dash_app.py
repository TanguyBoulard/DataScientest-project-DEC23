import os
import time
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
from datetime import datetime, timedelta

from dotenv import load_dotenv
from requests import RequestException

from utils.api_endpoints import get_token, get_data

# Initialize Dash app
dash_app = dash.Dash(__name__, requests_pathname_prefix='/dashboard/')
dash_app.title = 'Weather Dashboard'

load_dotenv()
BASE_URL = 'http://localhost:8000'
USERNAME = os.getenv('API_USER')
PASSWORD = os.getenv('API_PASSWORD')

# Initialize token as None
token = None

# Function to get token
def get_api_token(base_url, username, password):
    global token

    max_retries = 5

    if token is not None:
        return token

    for attempt in range(max_retries):
        try:
            token = get_token(base_url, username, password)
            return token
        except RequestException:
            if attempt < max_retries - 1:
                time.sleep(5)
    raise RequestException('Unable to fetch token')

# Layout
dash_app.layout = html.Div([
    html.H1('Weather Dashboard'),
    dcc.Dropdown(id='city-dropdown', options=[], value='Sydney', style={'width': '50%'}),
    dcc.DatePickerRange(
        id='date-range',
        start_date=datetime.now().date() - timedelta(days=30),
        end_date=datetime.now().date(),
        display_format='YYYY-MM-DD'
    ),
    dcc.Graph(id='weather-graph'),
    html.Div([html.H3('Weather Statistics'), html.Div(id='weather-stats')]),
    html.Div([html.H3('Rain Prediction for Tomorrow'), html.Div(id='rain-prediction')])
])

def fetch_weather_data(token, city, start_date, end_date):
    params = {'city': city, 'start_date': start_date, 'end_date': end_date}
    response = get_data(BASE_URL, 'weather', token, params)
    return pd.DataFrame(response)

def create_weather_graph(df, city):
    fig = go.Figure()
    for column in ['max_temp', 'min_temp', 'rainfall', 'humidity_9am', 'humidity_3pm']:
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column.replace('_', ' ').title()))
    fig.update_layout(
        title=f'Weather Data for {city}',
        xaxis_title='Date',
        yaxis_title='Value',
        legend_title='Parameter'
    )
    return fig

def calculate_weather_stats(df):
    return [
        html.P(f"Average Maximum Temperature: {df['max_temp'].mean():.2f}°C"),
        html.P(f"Average Minimum Temperature: {df['min_temp'].mean():.2f}°C"),
        html.P(f"Total Rainfall: {df['rainfall'].sum():.2f} mm"),
        html.P(f"Average Humidity at 9AM: {df['humidity_9am'].mean():.2f}%"),
        html.P(f"Average Humidity at 3PM: {df['humidity_3pm'].mean():.2f}%")
    ]

def get_rain_prediction(token, city):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        params = {'city': city, 'date': tomorrow}
        prediction = get_data(BASE_URL, 'predict', token, params)
        return html.P(f"Rain prediction for tomorrow ({tomorrow}): {prediction['rain_tomorrow']}")
    except requests.RequestException as e:
        print(f"Error fetching prediction: {e}")
        return html.P(f"Unable to fetch rain prediction: {str(e)}")

@dash_app.callback(
    Output('city-dropdown', 'options'),
    Input('city-dropdown', 'search_value')
)
def update_cities(search_value):
    cities = get_data(BASE_URL, 'cities', '', {})
    return [{'label': city['name'], 'value': city['name']} for city in cities]

@dash_app.callback(
    [Output('weather-graph', 'figure'),
     Output('weather-stats', 'children'),
     Output('rain-prediction', 'children')],
    [Input('city-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(city, start_date, end_date):
    api_token = get_api_token(BASE_URL, USERNAME, PASSWORD)
    df = fetch_weather_data(api_token, city, start_date, end_date)
    graph = create_weather_graph(df, city)
    stats = calculate_weather_stats(df)
    prediction = get_rain_prediction(api_token, city)
    return graph, stats, prediction
