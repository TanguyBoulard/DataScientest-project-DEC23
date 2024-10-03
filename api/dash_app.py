import os
import time
from datetime import datetime, timedelta
from functools import wraps

import dash
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output
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

# Initialize token and expiration time
token = None
token_expiration = None


def get_api_token() -> str:
    """
    Get or refresh the API token.

    Returns:
        str: The valid API token.

    Raises:
        RequestException: If unable to fetch the token after multiple attempts.
    """
    global token, token_expiration

    # Check if token is still valid
    if token and token_expiration and datetime.now() < token_expiration:
        return token

    max_retries = 5
    for attempt in range(max_retries):
        try:
            token = get_token(BASE_URL, USERNAME, PASSWORD)
            token_expiration = datetime.now() + timedelta(minutes=30)
            return token
        except RequestException:
            if attempt < max_retries - 1:
                time.sleep(5)
    raise RequestException('Unable to fetch token')


def token_required(func):
    """
    Decorator to ensure a valid token is available before making API calls that require authentication.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The wrapped function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            kwargs['token'] = get_api_token()
            return func(*args, **kwargs)
        except RequestException as e:
            print(f"Error refreshing token: {e}")
            return None
    return wrapper


def fetch_weather_data(city: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch weather data from the API.

    Args:
        city (str): The city for which to fetch weather data.
        start_date (str): The start date of the data range.
        end_date (str): The end date of the data range.

    Returns:
        pd.DataFrame: A DataFrame containing the weather data.

    Raises:
        Exception: If no weather data is received.
    """
    params = {'city': city, 'start_date': start_date, 'end_date': end_date}
    response = get_data(BASE_URL, 'weather', '', params)
    if not response:
        raise Exception('No weather data received')
    return pd.DataFrame(response)


def create_weather_graph(df: pd.DataFrame, city: str) -> go.Figure:
    """
    Create a weather graph using the provided data.

    Args:
        df (pd.DataFrame): The weather data.
        city (str): The city for which the graph is created.

    Returns:
        go.Figure: A Plotly figure object representing the weather graph.
    """
    fig = go.Figure()
    for column in ['max_temp', 'min_temp', 'rainfall', 'humidity_9am', 'humidity_3pm']:
        fig.add_trace(go.Scatter(x=df['date'], y=df[column], name=column.replace('_', ' ').title()))
    fig.update_layout(
        title=f"Weather Data for {city}",
        xaxis_title='Date',
        yaxis_title='Value',
        legend_title='Parameter'
    )
    return fig


def calculate_weather_stats(df: pd.DataFrame) -> list:
    """
    Calculate weather statistics from the provided data.

    Args:
        df (pd.DataFrame): The weather data.

    Returns:
        list: A list of HTML paragraph elements containing weather statistics.

    Raises:
        Exception: If no weather data is available for statistics.
    """
    if df.empty:
        raise Exception('No weather data available for statistics')
    return [
        html.P(f"Average Maximum Temperature: {df['max_temp'].mean():.2f}°C"),
        html.P(f"Average Minimum Temperature: {df['min_temp'].mean():.2f}°C"),
        html.P(f"Total Rainfall: {df['rainfall'].sum():.2f} mm"),
        html.P(f"Average Humidity at 9AM: {df['humidity_9am'].mean():.2f}%"),
        html.P(f"Average Humidity at 3PM: {df['humidity_3pm'].mean():.2f}%")
    ]


@token_required
def get_rain_prediction(city: str, token: str) -> html.P:
    """
    Get rain prediction for tomorrow.

    Args:
        city (str): The city for which to get the prediction.
        token (str): The API token for authentication.

    Returns:
        html.P: An HTML paragraph element containing the rain prediction.
    """
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    params = {'city': city, 'date': tomorrow}
    prediction = get_data(BASE_URL, 'predict', token, params)
    return html.P(
        f"Rain prediction for tomorrow ({tomorrow}) at {city}: {prediction['rain_tomorrow']}")


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


@dash_app.callback(
    Output('city-dropdown', 'options'),
    Input('city-dropdown', 'search_value')
)
def update_cities(search_value):
    try:
        cities = get_data(BASE_URL, 'cities', '', {})
        return [{'label': city['name'], 'value': city['name']} for city in cities]
    except Exception:
        return []


@dash_app.callback(
    [Output('weather-graph', 'figure'),
     Output('weather-stats', 'children'),
     Output('rain-prediction', 'children')],
    [Input('city-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(city: str, start_date: str, end_date: str):
    """
    Update the dashboard with weather data and predictions.

    Args:
        city (str): The selected city.
        start_date (str): The start date of the data range.
        end_date (str): The end date of the data range.

    Returns:
        tuple: A tuple containing the updated graph, weather statistics, and rain prediction.
    """
    graph = go.Figure()  # Empty figure as fallback
    stats = html.P('No weather statistics available.')
    prediction = html.P('No rain prediction available.')

    try:
        df = fetch_weather_data(city, start_date, end_date)
        graph = create_weather_graph(df, city)
        stats = calculate_weather_stats(df)
        prediction = get_rain_prediction(city)
    except Exception as e:
        print(f"Error updating dashboard: {e}")

    return graph, stats, prediction
