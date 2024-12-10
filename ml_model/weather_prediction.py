import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import plotly.express as px
from datetime import datetime, timedelta
import joblib
from dotenv import load_dotenv
from .data_collector import Weather_Data_Collector
import os
from time import sleep
import traceback
import requests
import pickle
import math
import random


load_dotenv()


class Weather_Prediction:
    def __init__(self):
        self.models = {}
        self.model_names = {
            'temperature': 'temperature',  # Changed from 'temp' to 'temperature'
            'humidity': 'humidity',
            'pressure': 'pressure',
            'wind_speed': 'wind_speed'
        }
        self.feature_names = ['temperature', 'humidity', 'pressure', 'wind_speed']  # Updated to match
        
        # Load models
        for param_short, param_file in self.model_names.items():
            model_path = f'models/{param_file}_model.joblib'
            try:
                self.models[param_short] = joblib.load(model_path)
                print(f"Successfully loaded {param_file} model")
            except Exception as e:
                print(f"Error loading {param_file} model: {str(e)}")

    def prepare_input_data(self, weather_data):
        try:
            # Extract basic features from weather data
            basic_features = {
                'temperature': weather_data['main']['temp'],  # Changed from 'temp' to 'temperature'
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure'],
                'wind_speed': weather_data['wind']['speed']
            }
            
            # Create extended feature set (17 features)
            current_hour = datetime.now().hour
            
            extended_features = [
                basic_features['temperature'],          # Current temperature
                basic_features['humidity'],      # Current humidity
                basic_features['pressure'],      # Current pressure
                basic_features['wind_speed'],    # Current wind speed
                math.sin(2 * math.pi * current_hour / 24),  # Hour of day (sine)
                math.cos(2 * math.pi * current_hour / 24),  # Hour of day (cosine)
                basic_features['temperature'] ** 2,     # Temperature squared
                basic_features['humidity'] ** 2, # Humidity squared
                basic_features['pressure'] - 1013.25,  # Pressure deviation from standard
                basic_features['wind_speed'] ** 2,     # Wind speed squared
                basic_features['temperature'] * basic_features['humidity'],  # Temp-humidity interaction
                basic_features['temperature'] * basic_features['wind_speed'],  # Temp-wind interaction
                basic_features['humidity'] * basic_features['wind_speed'],  # Humidity-wind interaction
                math.sin(2 * math.pi * current_hour / 12),  # 12-hour cycle (sine)
                math.cos(2 * math.pi * current_hour / 12),  # 12-hour cycle (cosine)
                basic_features['pressure'] * basic_features['wind_speed'],  # Pressure-wind interaction
                float(current_hour)  # Hour as numeric feature
            ]
            
            return np.array([extended_features])
            
        except Exception as e:
            print(f"Error preparing input data: {str(e)}")
            traceback.print_exc()
            return None

    def predict(self, city):
        try:
            # Get current weather data
            weather_data = self.get_weather_data(city)
            if weather_data is None:
                return None

            # Prepare input data
            input_data = self.prepare_input_data(weather_data)
            if input_data is None:
                return None

            # Get initial pressure for more realistic variations
            initial_pressure = weather_data['main']['pressure']
            
            # Make predictions
            predictions = []
            current_time = datetime.now()

            for i in range(24):
                prediction_time = current_time + timedelta(hours=i)
                
                # Make predictions for each parameter
                pred = {
                    'timestamp': prediction_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                for param in self.feature_names:
                    pred[param] = float(self.models[param].predict(input_data)[0])
                
                # Add time-based variations
                hour = prediction_time.hour
                
                # Temperature variation
                pred['temperature'] += math.sin(hour * math.pi / 12) * 2
                
                # Humidity variation (inverse to temperature)
                pred['humidity'] += -math.sin(hour * math.pi / 12) * 5
                
                # Pressure variation (more realistic)
                time_factor = i / 24.0  # Normalized time factor
                random_factor = random.uniform(-0.3, 0.3)  # Small random variation
                trend_factor = math.sin(2 * math.pi * time_factor) * 0.7  # Sinusoidal trend
                
                # Calculate pressure based on initial value with variations
                pred['pressure'] = initial_pressure + trend_factor + random_factor
                
                # Wind speed with more variation
                pred['wind_speed'] += random.uniform(-0.8, 0.8)
                
                # Ensure values are within reasonable ranges
                pred['temperature'] = max(-10, min(40, pred['temperature']))
                pred['humidity'] = max(0, min(100, pred['humidity']))
                pred['pressure'] = max(980, min(1040, pred['pressure']))  # Standard range for pressure
                pred['wind_speed'] = max(0, min(20, pred['wind_speed']))
                
                predictions.append(pred)

            return predictions

        except Exception as e:
            print(f"Error in predict method: {str(e)}")
            traceback.print_exc()
            return None

    def get_weather_data(self, city):
        try:
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                print("Error: OpenWeather API key not found")
                return None

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            return None