"""
This script is used to scrape the Australian Bureau of Meteorology website
"""

import numpy as np
from dotenv import load_dotenv
from itertools import product
import re
from typing import Optional, Tuple
import requests
from datetime import datetime, timedelta
from typing import List
import pandas as pd
from bs4 import BeautifulSoup
from database.postgresql_functools import PostgresManager
from utils.df_to_kaggle_format import transform_to_kaggle_format


def generate_urls(dates: List[str], locations: List[str]) -> List[str]:
    """
    Generates URLs for weather data based on specified dates and locations.

    Documentation:
        Further details on the website can be found at:
            https://reg.bom.gov.au

    :param dates: List of dates for which to fetch weather data.
    :param locations: List of location codes to fetch weather data for.
    :returns: List of URLs constructed based on the specified dates and locations.
    """
    # Base URL for the Australian Bureau of Meteorology website's weather data
    base_url = ("https://reg.bom.gov.au/climate/dwo/{date}/"
                "html/IDCJDW{location}.{date}.shtml")
    # Create URLs for all combinations of dates and locations
    return [base_url.format(date=date, location=location)
            for date, location in product(dates, locations)]


def fetch_page_content(url: str) -> Optional[BeautifulSoup]:
    """
    Fetches the HTML content from a given URL.

    :param url: The URL from which to fetch the content.
    :returns: BeautifulSoup object containing the parsed HTML content,
        or None if the request fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad responses
        # Parse and return the HTML content
        bs = BeautifulSoup(response.content, 'lxml')
        return bs
    except requests.RequestException as e:
        # Print the error if request fails
        print(f"Error fetching URL {url}: {e}")
        return None


def extract_simplified_information(html: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts simplified location and date information from the HTML
    content of a page.

    :param html: HTML content as a string.
    :returns: A tuple containing the location and date, or None if not found.
    """
    # Use regular expression to extract location and date in the HTML content
    match = re.search(r"<h1>(?P<location>.+?)(?:<br/?>|,)\s*"
                      r"(?P<date>\w+ \d{4})", html, re.IGNORECASE)
    if match:
        # Extract location
        location = match.group('location').split(',')[0].strip()
        # Extract date
        date = match.group('date').strip()
        return location, date
    return None, None  # Return a tuple of None if no match is found


def parse_html_content(soup: BeautifulSoup) -> pd.DataFrame:
    """
    Parses the HTML content with BeautifulSoup and extracts
    the weather data into a DataFrame.

    :param soup: BeautifulSoup object containing the parsed HTML content.
    :return: DataFrame containing the extracted weather data.
    """
    # Extract the page header to get location and date information
    header = soup.find('div', attrs={'class': 'content'}).find('h1')
    location, date = extract_simplified_information(str(header))

    # Find the table containing the weather data
    table = soup.find('table', attrs={'class': 'data'})
    rows = table.find('tbody').find_all('tr')  # Extract all table rows

    # Extract day indexes from table headers
    days = [index.text for row in rows for index in row.find_all('th')]

    # Compile the data for each day from the table rows
    data = [[cell.text if cell.text != '\xa0' else np.nan
             for cell in row.find_all('td')]
            for row in rows]

    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == 'Calm':
                data[i].insert(j + 1, -1)

    # Convert date string to datetime and format dates for each day
    month_year_datetime = datetime.strptime(date, "%B %Y")
    formatted_dates = [month_year_datetime.replace(day=int(day))
                       .strftime("%Y-%m-%d") for day in days]

    # Define the columns for the DataFrame
    columns = ['day', 'min_temp', 'max_temp', 'rainfall',
               'evaporation', 'sunshine', 'wind_gust_dir',
               'wind_gust_speed', 'wind_gust_time', 'temp_9am',
               'humidity_9am', 'cloud_9am', 'wind_dir_9am',
               'wind_speed_9am', 'pressure_9am', 'temp_3pm',
               'humidity_3pm', 'cloud_3pm', 'wind_dir_3pm',
               'wind_speed_3pm', 'pressure_3pm']
    df = pd.DataFrame(data, columns=columns)

    # Drop unnecessary columns
    df.drop(['day', 'wind_gust_time'], axis=1, inplace=True)

    df['date'] = formatted_dates
    df['location'] = location

    return df


def aggregate_weather_data(urls: List[str]) -> pd.DataFrame:
    """
    Aggregates weather data from multiple URLs into a single DataFrame.

    :param urls: List of URLs to fetch and parse weather data from.
    :return: Aggregated DataFrame containing weather data from all specified URLs.
    """
    aggregated_df = pd.DataFrame()
    for url in urls:
        soup = fetch_page_content(url)
        if soup:
            # Extract weather data into a DataFrame
            df_temp = parse_html_content(soup)
            aggregated_df = pd.concat([aggregated_df, df_temp],
                                      ignore_index=True)
    return aggregated_df


def scrap_weather_data(dates_to_scrape: List[str]) -> None:
    """
    Scrapes the Australian Bureau of Meteorology website for weather data
    :param dates_to_scrape: Define the dates to scrape: <year><month>
    """
    # Define the locations to scrape: <location>: <location_id_on_website>
    locations_to_scrape = {'Canberra': '2801',
                           'Sydney': '2124',
                           'Darwin': '8014',
                           'Melbourne': '3033',
                           'Brisbane': '4019'}

    # Generate the URLs to scrape
    pages_to_scrape = generate_urls(dates_to_scrape, list(locations_to_scrape.values()))

    # Aggregate the weather data
    weather_scrapped = aggregate_weather_data(pages_to_scrape) \
        .replace({'Melbourne (Olympic Park)': 'Melbourne',
                  'Brisbane': 'Brisbane City'})

    daily_weather, weather_9am, weather_3pm = transform_to_kaggle_format(weather_scrapped,
                                                                         postgres)

    # Store the weather data to data warehouse
    daily_weather.to_sql('daily_weather', postgres.engine, if_exists='append', index=False)
    weather_9am.to_sql('weather', postgres.engine, if_exists='append', index=False)
    weather_3pm.to_sql('weather', postgres.engine, if_exists='append', index=False)


if __name__ == '__main__':
    load_dotenv()
    postgres = PostgresManager()

    # Calculate the last 12 months from the current date
    current_date = datetime.now()
    dates_to_scrape = [(current_date - timedelta(days=30 * i)).strftime('%Y%m') for i in range(12)]

    scrap_weather_data(dates_to_scrape)
