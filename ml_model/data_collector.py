import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Weather_Data_Collector:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenWeather API key not found!")
            
        # Direct weather API endpoint (this is the key change)
        self.weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    def get_current_weather(self, city):
        """
        Get current weather directly using city name
        """
        try:
            # Direct city query (simpler and more reliable)
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # For Celsius
            }
            
            response = requests.get(self.weather_url, params=params)
            
            # Debug information
            print(f"Request URL: {response.url}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                weather_info = {
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': round(data['main']['temp'], 1),
                    'feels_like': round(data['main']['feels_like'], 1),
                    'temp_min': round(data['main']['temp_min'], 1),
                    'temp_max': round(data['main']['temp_max'], 1),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'timestamp': datetime.fromtimestamp(data['dt']),
                    'clouds': data['clouds']['all']
                }
                return weather_info
            
            elif response.status_code == 404:
                print(f"City not found: {city}")
                return None
            else:
                print(f"API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting weather: {str(e)}")
            return None

    def get_forecast(self, city):
        """
        Get 5-day forecast directly using city name
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.forecast_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                forecast_list = []
                
                for item in data['list']:
                    forecast_item = {
                        'timestamp': datetime.fromtimestamp(item['dt']),
                        'temperature': round(item['main']['temp'], 1),
                        'feels_like': round(item['main']['feels_like'], 1),
                        'temp_min': round(item['main']['temp_min'], 1),
                        'temp_max': round(item['main']['temp_max'], 1),
                        'humidity': item['main']['humidity'],
                        'pressure': item['main']['pressure'],
                        'wind_speed': item['wind']['speed'],
                        'description': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon'],
                        'clouds': item['clouds']['all']
                    }
                    forecast_list.append(forecast_item)
                    
                return forecast_list
            
            return None
            
        except Exception as e:
            print(f"Error getting forecast: {str(e)}")
            return None

    def get_3hour_forecast(self, city):
        """
        Get 5-day/3-hour forecast data using city name
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.forecast_url, params=params)
            
            print(f"Forecast request URL: {response.url}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                forecast_list = []
                
                for item in data['list']:
                    forecast_item = {
                        'timestamp': datetime.fromtimestamp(item['dt']),
                        'temperature': round(item['main']['temp'], 1),
                        'feels_like': round(item['main']['feels_like'], 1),
                        'temp_min': round(item['main']['temp_min'], 1),
                        'temp_max': round(item['main']['temp_max'], 1),
                        'humidity': item['main']['humidity'],
                        'pressure': item['main']['pressure'],
                        'wind_speed': item['wind']['speed'],
                        'description': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon'],
                        'clouds': item['clouds']['all'],
                        'pop': round(item.get('pop', 0) * 100),  # Probability of precipitation
                        'rain_3h': item.get('rain', {}).get('3h', 0),  # Rain volume for last 3 hours
                        'snow_3h': item.get('snow', {}).get('3h', 0)   # Snow volume for last 3 hours
                    }
                    forecast_list.append(forecast_item)
                    
                return forecast_list
            
            elif response.status_code == 404:
                print(f"City not found: {city}")
                return None
            else:
                print(f"API Error: {response.status_code}")
                return None
            
        except Exception as e:
            print(f"Error getting 3-hour forecast: {str(e)}")
            return None

    def group_forecast_by_day(self, forecast_data):
        """
        Group 3-hour forecast data into daily summaries
        """
        if not forecast_data:
            return None
        
        try:
            daily_forecast = {}
            
            for item in forecast_data:
                date = item['timestamp'].date()
                
                if date not in daily_forecast:
                    daily_forecast[date] = {
                        'temp_min': float('inf'),
                        'temp_max': float('-inf'),
                        'humidity': [],
                        'pressure': [],
                        'wind_speed': [],
                        'descriptions': [],
                        'icons': [],
                        'pop': [],
                        'rain_3h': [],
                        'snow_3h': []
                    }
                
                # Update daily statistics
                daily_forecast[date]['temp_min'] = min(daily_forecast[date]['temp_min'], item['temp_min'])
                daily_forecast[date]['temp_max'] = max(daily_forecast[date]['temp_max'], item['temp_max'])
                daily_forecast[date]['humidity'].append(item['humidity'])
                daily_forecast[date]['pressure'].append(item['pressure'])
                daily_forecast[date]['wind_speed'].append(item['wind_speed'])
                daily_forecast[date]['descriptions'].append(item['description'])
                daily_forecast[date]['icons'].append(item['icon'])
                daily_forecast[date]['pop'].append(item['pop'])
                daily_forecast[date]['rain_3h'].append(item.get('rain_3h', 0))
                daily_forecast[date]['snow_3h'].append(item.get('snow_3h', 0))
            
            # Calculate daily summaries
            formatted_daily = []
            for date, data in daily_forecast.items():
                formatted_daily.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'temp_min': round(data['temp_min'], 1),
                    'temp_max': round(data['temp_max'], 1),
                    'humidity': round(sum(data['humidity']) / len(data['humidity'])),
                    'pressure': round(sum(data['pressure']) / len(data['pressure'])),
                    'wind_speed': round(sum(data['wind_speed']) / len(data['wind_speed']), 1),
                    'description': max(set(data['descriptions']), key=data['descriptions'].count),
                    'icon': max(set(data['icons']), key=data['icons'].count),
                    'pop': round(max(data['pop'])),  # Maximum probability of precipitation
                    'rain': round(sum(data['rain_3h']), 1),  # Total rain
                    'snow': round(sum(data['snow_3h']), 1)   # Total snow
                })
            
            return formatted_daily
            
        except Exception as e:
            print(f"Error grouping forecast data: {str(e)}")
            return None

# Test function
def test_weather_api():
    try:
        collector = Weather_Data_Collector()
        
        # Test cities
        test_cities = ["London", "Paris", "New York", "Tokyo"]
        
        for city in test_cities:
            print(f"\nTesting weather for {city}...")
            
            # Test current weather
            current = collector.get_current_weather(city)
            if current:
                print(f"Current temperature in {city}: {current['temperature']}°C")
                print(f"Description: {current['description']}")
            else:
                print(f"Failed to get current weather for {city}")
                continue
            
            # Test forecast
            forecast = collector.get_forecast(city)
            if forecast:
                print(f"Successfully got forecast with {len(forecast)} entries")
            else:
                print(f"Failed to get forecast for {city}")

    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_weather_api()


