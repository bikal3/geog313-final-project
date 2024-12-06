import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_openmeteo_data(latitude, longitude, start_date, end_date, variables, timezone="GMT", model="gfs_seamless"):
    """
    Fetch and process weather data from the Open-Meteo API.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        variables (list): List of variables to fetch (e.g., 'temperature_2m_max', 'precipitation_sum').
        timezone (str): Timezone of the data (default: "GMT").
        model (str): Weather model to use (default: "gfs_seamless").

    Returns:
        pd.DataFrame: DataFrame containing requested variables and their values.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": variables,
        "timezone": timezone,
        "start_date": start_date,
        "end_date": end_date,
        "models": model
    }
    
    # Fetch data from the Open-Meteo API
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]  # Process the first response (can be extended for multiple locations)
    
    # Extract daily data
    daily = response.Daily()
    data = {}
    
    # Assign requested variables dynamically
    for i, variable in enumerate(variables):
        data[variable] = daily.Variables(i).ValuesAsNumpy()
    
    # Add date range
    data["date"] = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df