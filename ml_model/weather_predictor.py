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


class Weather_Prediction():
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.target_variables = ['temperature', 'humidity', 'pressure', 'wind_speed']
        
        # Get the absolute path to the models directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, '..', 'models')
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        try:
            self.load_models()
        except Exception as e:
            print(f"Error initializing models: {str(e)}")
            self.train_models()  # Train new models if loading fails

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

            # Make predictions with realistic variations
            predictions = []
            current_time = datetime.now()
            
            # Get base predictions from the model
            base_temp = float(self.models['temperature'].predict(input_data)[0])
            base_humidity = float(self.models['humidity'].predict(input_data)[0])
            base_pressure = float(self.models['pressure'].predict(input_data)[0])
            base_wind = float(self.models['wind_speed'].predict(input_data)[0])

            for i in range(24):
                prediction_time = current_time + timedelta(hours=i)
                hour = prediction_time.hour
                
                # Add daily variations
                temp_variation = math.sin(hour * math.pi / 12) * 2  # ±2°C daily variation
                humidity_variation = -math.sin(hour * math.pi / 12) * 5  # ±5% inverse to temperature
                pressure_variation = math.sin(i * math.pi / 12) * 0.5  # Slight pressure variations
                wind_variation = random.uniform(-0.5, 0.5)  # Random wind variations
                
                pred = {
                    'timestamp': prediction_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': max(0, base_temp + temp_variation),
                    'humidity': max(0, min(100, base_humidity + humidity_variation)),
                    'pressure': base_pressure + pressure_variation,
                    'wind_speed': max(0, base_wind + wind_variation)
                }
                predictions.append(pred)

            return predictions

        except Exception as e:
            print(f"Error in predict method: {str(e)}")
            return None

    def get_weather_data(self, city):
        try:
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                print("Error: OpenWeather API key not found")
                return None

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required fields
                required_fields = {
                    'main': ['temp', 'humidity', 'pressure'],
                    'wind': ['speed']
                }
                
                for section, fields in required_fields.items():
                    if section not in data:
                        print(f"Missing section: {section}")
                        return None
                    for field in fields:
                        if field not in data[section]:
                            print(f"Missing field: {field} in {section}")
                            return None
                
                print("Valid weather data received:", data)
                return data
                
            else:
                print(f"API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            return None

    def prepare_input_data(self, weather_data):
        try:
            import pandas as pd
            from datetime import datetime
            
            if weather_data is None:
                print("Error: No weather data provided")
                return None

            # Get current timestamp
            current_time = datetime.fromtimestamp(weather_data['dt'])
            
            # Get feature order from scaler
            if hasattr(self.scaler, 'feature_names_in_'):
                feature_order = self.scaler.feature_names_in_.tolist()
            else:
                raise Exception("Scaler does not have feature_names_in_ attribute")
            
            # Create feature dictionary
            features = {
                'clouds': weather_data['clouds']['all'],
                'day': current_time.day,
                'day_of_week': current_time.weekday(),
                'hour': current_time.hour,
                'humidity': weather_data['main']['humidity'],
                'humidity_lag1': weather_data['main']['humidity'],
                'humidity_lag2': weather_data['main']['humidity'],
                'month': current_time.month,
                'pressure': weather_data['main']['pressure'],
                'pressure_lag1': weather_data['main']['pressure'],
                'pressure_lag2': weather_data['main']['pressure'],
                'temperature': weather_data['main']['temp'],
                'temperature_lag1': weather_data['main']['temp'],
                'temperature_lag2': weather_data['main']['temp'],
                'wind_speed': weather_data['wind']['speed'],
                'wind_speed_lag1': weather_data['wind']['speed'],
                'wind_speed_lag2': weather_data['wind']['speed']
            }
            
            # Create DataFrame with features in exact order from scaler
            features_df = pd.DataFrame([features])[feature_order]
            
            # Debug prints
            print("Scaler feature order:", feature_order)
            print("DataFrame feature order:", features_df.columns.tolist())
            
            # Transform data
            scaled_features = self.scaler.transform(features_df)
            return scaled_features

        except Exception as e:
            print(f"Error preparing input data: {str(e)}")
            print("Available features:", features.keys())
            return None

    def load_models(self):
        try:
            print(f"\nLoading models from: {self.model_path}")
            
            # Load scaler
            scaler_path = os.path.join(self.model_path, 'scaler.joblib')
            self.scaler = joblib.load(scaler_path)
            
            # Print feature names from scaler
            if hasattr(self.scaler, 'feature_names_in_'):
                print("Scaler feature names:", self.scaler.feature_names_in_.tolist())
            
            # Load models for each target variable
            for target in self.target_variables:
                model_file = os.path.join(self.model_path, f'{target}_model.joblib')
                self.models[target] = joblib.load(model_file)

            print("Models loaded successfully")
            
        except Exception as e:
            print(f"Error loading models: {str(e)}")
            print("Full error details:", traceback.format_exc())
            raise Exception(f"Failed to load models: {str(e)}")

    def train_models(self):
        try:
            print("\nTraining new models...")
            
            # Create dummy data for initial models
            # This is a temporary solution - replace with actual training data
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler
            import numpy as np
            
            # Generate dummy training data
            X_train = np.random.rand(100, 4)  # 4 features
            y_train = np.random.rand(100)
            
            # Train scaler
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X_train)
            
            # Save scaler
            scaler_path = os.path.join(self.model_path, 'scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Train and save models for each target
            for target in self.target_variables:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_scaled, y_train)
                self.models[target] = model
                
                # Save model
                model_path = os.path.join(self.model_path, f'{target}_model.pkl')
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            
            print("New models trained and saved successfully")
            
        except Exception as e:
            print(f"Error training models: {str(e)}")
            print("Full error details:", traceback.format_exc())
            raise Exception(f"Failed to train models: {str(e)}")

    def evaluate_predictions(self, city, hours=24):
        """
        Evaluate prediction accuracy
        """
        try:
            # Get actual data
            forecast = self.data_collector.get_3hour_forecast(city)
            if not forecast:
                return None
            
            # Get current weather for initial conditions
            current = self.data_collector.get_current_weather(city)
            if not current:
                return None
            
            # Make predictions
            predictions = self.predict(current, hours)
            if not predictions:
                return None
            
            # Compare predictions with actual values
            results = {}
            for target in self.target_variables:
                actual = [item[target] for item in forecast[:8]]  # First 24 hours
                predicted = [item[target] for item in predictions[:8]]
                
                mse = mean_squared_error(actual, predicted)
                results[target] = {
                    'mse': mse,
                    'rmse': np.sqrt(mse),
                    'actual': actual,
                    'predicted': predicted
                }
            
            return results
            
        except Exception as e:
            print(f"Error evaluating predictions: {e}")
            return None

    def save_training_data(self, data, city_list):
        """
        Save training data and predictions to CSV files with proper datetime handling
        """
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(self.model_path, '..', 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created data directory: {data_dir}")
            
            # Save raw training data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            training_file = os.path.join(data_dir, f'training_data_{timestamp}.csv')
            
            # Convert datetime columns to string
            data_copy = data.copy()
            for column in data_copy.columns:
                if isinstance(data_copy[column].iloc[0], datetime):
                    data_copy[column] = data_copy[column].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Add city column
            data_copy['city'] = data_copy['city'] if 'city' in data_copy.columns else 'Unknown'
            
            # Save to CSV
            data_copy.to_csv(training_file, index=False)
            print(f"\nTraining data saved to: {training_file}")
            
            # Save training metadata
            metadata_file = os.path.join(data_dir, f'training_metadata_{timestamp}.csv')
            metadata = pd.DataFrame({
                'city': city_list,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'features': [', '.join(self.features)] * len(city_list),
                'target_variables': [', '.join(self.target_variables)] * len(city_list)
            })
            metadata.to_csv(metadata_file, index=False)
            print(f"Training metadata saved to: {metadata_file}")
            
            return True
            
        except Exception as e:
            print(f"Error saving training data: {e}")
            return False

    def save_predictions(self, city, predictions):
        """
        Save predictions to CSV file with proper datetime handling
        """
        try:
            # Create predictions directory if it doesn't exist
            pred_dir = os.path.join(self.model_path, '..', 'predictions')
            if not os.path.exists(pred_dir):
                os.makedirs(pred_dir)
            
            # Convert predictions to DataFrame
            pred_df = pd.DataFrame(predictions)
            
            # Convert datetime columns to string
            for column in pred_df.columns:
                if isinstance(pred_df[column].iloc[0], datetime):
                    pred_df[column] = pred_df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Add city and prediction timestamp
            pred_df['city'] = city
            pred_df['prediction_made_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pred_file = os.path.join(pred_dir, f'predictions_{city}_{timestamp}.csv')
            pred_df.to_csv(pred_file, index=False)
            
            print(f"\nPredictions saved to: {pred_file}")
            return True
            
        except Exception as e:
            print(f"Error saving predictions: {e}")
            return False