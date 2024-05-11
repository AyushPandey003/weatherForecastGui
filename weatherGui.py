import tkinter as tk
from tkinter import ttk
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup caching and retrying sessions
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def fetch_weather():
    try:
        latitude = float(lat_entry.get())
        longitude = float(lon_entry.get())
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
            "hourly": "temperature_2m"
        }
        responses = openmeteo.weather_api(url, params=params)
        
        response = responses[0]
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()

        current_weather_label.config(text=f"Current temperature: {current_temperature_2m}°C")
        
        # Hourly Data
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end = pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, hourly_dataframe)
    
    except Exception as e:
        current_weather_label.config(text=f"Error: {str(e)}")

# Setup the GUI
root = tk.Tk()
root.title("Weather Forecast GUI")

# Latitude Entry
tk.Label(root, text="Enter latitude:").pack()
lat_entry = tk.Entry(root)
lat_entry.pack()

# Longitude Entry
tk.Label(root, text="Enter longitude:").pack()
lon_entry = tk.Entry(root)
lon_entry.pack()

# Button to fetch weather
fetch_button = ttk.Button(root, text="Fetch Weather", command=fetch_weather)
fetch_button.pack()

# Label to display current weather
current_weather_label = tk.Label(root, text="Current temperature:")
current_weather_label.pack()

# Text Area to display hourly data
text_area = tk.Text(root, height=10, width=50)
text_area.pack()

# Run the application
root.mainloop()
