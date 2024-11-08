import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 48.8534,
    "longitude": 2.3488,
    "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "weather_code"],
    "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
    "timezone": "auto"
}

responses = openmeteo.weather_api(url, params=params)
response = responses[0]

print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

hourly = response.Hourly()
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_localize(None),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_localize(None),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
    "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
    "dew_point_2m": hourly.Variables(2).ValuesAsNumpy(),
    "apparent_temperature": hourly.Variables(3).ValuesAsNumpy(),
    "precipitation_probability": hourly.Variables(4).ValuesAsNumpy(),
    "precipitation": hourly.Variables(5).ValuesAsNumpy(),
    "weather_code": hourly.Variables(6).ValuesAsNumpy()
}

hourly_dataframe = pd.DataFrame(data=hourly_data)
hourly_dataframe.to_excel("hourly.xlsx", index=False)

daily = response.Daily()
daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True).tz_localize(None),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True).tz_localize(None),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    ),
    "weather_code": daily.Variables(0).ValuesAsNumpy(),
    "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
    "temperature_2m_min": daily.Variables(2).ValuesAsNumpy()
}

daily_dataframe = pd.DataFrame(data=daily_data)
daily_dataframe.to_excel("daily.xlsx", index=False)


