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



load_dotenv()


class Weather_Prediction():
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.features = [
            'temperature', 'humidity', 'pressure', 
            'wind_speed', 'clouds', 'hour', 'day', 
            'month', 'day_of_week'
        ]
        self.target_variables = [
            'temperature', 'humidity', 'pressure',
            'wind_speed'
        ]
        self.all_features = (
            self.features +
            [f'{feature}_lag1' for feature in self.target_variables] +
            [f'{feature}_lag2' for feature in self.target_variables]
        )
        self.data_collector = Weather_Data_Collector()
        
        # Use absolute path for models
        self.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
        print(f"Models directory: {self.model_path}")
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
            print(f"Created models directory at {self.model_path}")

    def prepare_data(self, df):
        """
        Prepare data with consistent feature ordering
        """
        try:
            print(f"\nInitial data shape: {df.shape}")
            
            # Handle timestamp
            if 'timestamp' not in df.columns:
                df['timestamp'] = pd.to_datetime(datetime.now())
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add time-based features
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Fill missing values
            for col in self.target_variables:
                if col not in df.columns:
                    df[col] = 0
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            if 'clouds' not in df.columns:
                df['clouds'] = 0
            df['clouds'] = df['clouds'].fillna(0)
            
            # Add lag features
            for feature in self.target_variables:
                df[f'{feature}_lag1'] = df.groupby(df['timestamp'].dt.date)[feature].shift(1)
                df[f'{feature}_lag2'] = df.groupby(df['timestamp'].dt.date)[feature].shift(2)
            # Convert all feature columns to numeric
            print("\nConverting features to numeric...")
            for col in self.features:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill any remaining NaN with column mean or 0
                if df[col].isna().any():
                    if col in ['temperature', 'humidity', 'pressure', 'wind_speed']:
                        df[col] = df[col].fillna(df[col].mean())
                    else:
                        df[col] = df[col].fillna(0)
            
            # Add lag features with proper handling
            print("\nAdding lag features...")
            for feature in self.target_variables:
                df[f'{feature}_lag1'] = df.groupby(df['timestamp'].dt.date)[feature].shift(1)
                df[f'{feature}_lag2'] = df.groupby(df['timestamp'].dt.date)[feature].shift(2)
                
                # Fill NaN in lag features with the original values
                df[f'{feature}_lag1'] = df[f'{feature}_lag1'].fillna(df[feature])
                df[f'{feature}_lag2'] = df[f'{feature}_lag2'].fillna(df[feature])
            
            print("\nNaN values after processing:")
            print(df.isna().sum())
            
            # Verify data quality
            print(f"\nRows with any NaN: {df.isna().any(axis=1).sum()}")
            print(f"Total rows: {len(df)}")
            
            if len(df) < 10:  # Minimum required rows
                print("Error: Insufficient data rows!")
                return None
            
            print("\nFinal columns:", df.columns.tolist())
            print(f"Final data shape: {df.shape}")
            
            # Print sample of final data
            print("\nSample of prepared data:")
            print(df.head())
            
            return df
            
        except Exception as e:
            print(f"Error in prepare_data: {e}")
            print("\nDataFrame info:")
            print(df.info())
            return None

    def train(self, city_list, days=30):
        """
        Train models using data from multiple cities
        """
        try:
            all_data = []
            
            for city in city_list:
                print(f"\nProcessing {city}...")
                
                # Get current weather with retries
                retries = 3
                current = None
                while retries > 0 and current is None:
                    current = self.data_collector.get_current_weather(city)
                    if not current:
                        print(f"Retry getting current weather for {city}...")
                        retries -= 1
                        sleep(1)
                
                if not current:
                    print(f"Skipping {city} - could not get current weather data")
                    continue
                
                # Get forecast with retries
                retries = 3
                forecast = None
                while retries > 0 and forecast is None:
                    forecast = self.data_collector.get_3hour_forecast(city)
                    if not forecast:
                        print(f"Retry getting forecast for {city}...")
                        retries -= 1
                        sleep(1)
                
                if not forecast:
                    print(f"Skipping {city} - could not get forecast data")
                    continue
                
                # Create DataFrames
                current_df = pd.DataFrame([current])
                forecast_df = pd.DataFrame(forecast)
                
                # Print data info
                print(f"\nCurrent weather data for {city}:")
                print(current_df.info())
                print(f"\nForecast data for {city}:")
                print(forecast_df.info())
                
                # Combine data
                city_data = pd.concat([current_df, forecast_df], ignore_index=True)
                print(f"Combined data for {city}: {len(city_data)} rows")
                
                all_data.append(city_data)
            
            if not all_data:
                print("No valid data collected for any city")
                return False
            
            # Combine all city data
            print("\nCombining data from all cities...")
            training_data = pd.concat(all_data, ignore_index=True)
            print(f"Combined data shape: {training_data.shape}")
            
            # Prepare features
            training_data = self.prepare_data(training_data)
            if training_data is None:
                return False
            
            # Select features
            feature_columns = self.features + [f'{feature}_lag1' for feature in self.target_variables] + \
                             [f'{feature}_lag2' for feature in self.target_variables]
            
            X = training_data[feature_columns]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train models
            for target in self.target_variables:
                print(f"\nTraining model for {target}...")
                y = training_data[target]
                
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                model.fit(X_scaled, y)
                
                # Save model
                model_path = os.path.join(self.model_path, f'{target}_model.joblib')
                joblib.dump(model, model_path)
                self.models[target] = model
                
                # Print metrics
                y_pred = model.predict(X_scaled)
                mse = mean_squared_error(y, y_pred)
                r2 = r2_score(y, y_pred)
                print(f"MSE: {mse:.4f}")
                print(f"R2 Score: {r2:.4f}")
            
            # Save scaler
            scaler_path = os.path.join(self.model_path, 'scaler.joblib')
            joblib.dump(self.scaler, scaler_path)
            
            return True
            
        except Exception as e:
            print(f"Error during training: {e}")
            return False

    def predict(self, current_weather, hours=24):
        """
        Make predictions with data validation
        """
        try:
            print("\n=== Starting Prediction Process ===")
            
            # 1. Validate input data
            print("\nValidating input data:")
            required_fields = ['temperature', 'humidity', 'pressure', 'wind_speed']
            
            print("\nReceived weather data:")
            for key, value in current_weather.items():
                print(f"{key}: {value}")
            
            # Check for missing fields
            missing_fields = [field for field in required_fields if field not in current_weather]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Check for invalid values
            for field in required_fields:
                value = current_weather[field]
                try:
                    float_value = float(value)
                    if not -100 <= float_value <= 100 and field == 'temperature':
                        print(f"Warning: Unusual temperature value: {float_value}°C")
                    elif not 0 <= float_value <= 100 and field == 'humidity':
                        print(f"Warning: Invalid humidity value: {float_value}%")
                    elif not 900 <= float_value <= 1100 and field == 'pressure':
                        print(f"Warning: Unusual pressure value: {float_value}hPa")
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value for {field}: {value}")
            
            print("\nInput data validation successful!")
            
            # 2. Load models
            if not self.models:
                print("\nLoading models...")
                if not self.load_models():
                    raise Exception("Could not load models")
                print("Models loaded successfully")
            
            # 3. Create prediction DataFrame
            try:
                print("\nCreating prediction DataFrame...")
                current_data = pd.DataFrame([{
                    'temperature': float(current_weather['temperature']),
                    'humidity': float(current_weather['humidity']),
                    'pressure': float(current_weather['pressure']),
                    'wind_speed': float(current_weather['wind_speed']),
                    'clouds': float(current_weather.get('clouds', 0)),
                    'hour': datetime.now().hour,
                    'day': datetime.now().day,
                    'month': datetime.now().month,
                    'day_of_week': datetime.now().weekday()
                }])
                
                print("\nInitial data:")
                print(current_data.head())
                print("\nData types:")
                print(current_data.dtypes)
                
            except Exception as e:
                print(f"Error creating DataFrame: {e}")
                raise
            
            # 4. Add lag features
            print("\nAdding lag features...")
            for feature in self.target_variables:
                current_data[f'{feature}_lag1'] = current_data[feature]
                current_data[f'{feature}_lag2'] = current_data[feature]
            
            # 5. Verify feature alignment
            print("\nVerifying features...")
            print("Expected features:", self.all_features)
            print("Current features:", current_data.columns.tolist())
            
            current_data = current_data.reindex(columns=self.all_features, fill_value=0)
            
            # 6. Make predictions
            print("\nMaking predictions...")
            predictions = []
            
            for hour in range(hours):
                future_time = datetime.now() + timedelta(hours=hour)
                
                # Update time features
                current_data['hour'] = future_time.hour
                current_data['day'] = future_time.day
                current_data['month'] = future_time.month
                current_data['day_of_week'] = future_time.weekday()
                
                try:
                    # Scale features
                    X_scaled = self.scaler.transform(current_data)
                    
                    # Create prediction
                    prediction = {
                        'timestamp': future_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Make predictions for each target
                    for target in self.target_variables:
                        predicted_value = float(self.models[target].predict(X_scaled)[0])
                        prediction[target] = round(predicted_value, 2)
                        
                        # Update lag features
                        current_data[f'{target}_lag2'] = current_data[f'{target}_lag1']
                        current_data[f'{target}_lag1'] = predicted_value
                        current_data[target] = predicted_value
                    
                    predictions.append(prediction)
                    
                    # Print first prediction as sample
                    if hour == 0:
                        print("\nFirst prediction:")
                        print(prediction)
                    
                except Exception as e:
                    print(f"Error during prediction for hour {hour}: {e}")
                    raise
            
            print(f"\nSuccessfully generated {len(predictions)} predictions")
            return predictions
            
        except Exception as e:
            print("\n=== Prediction Error Details ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nDebug information:")
            if 'current_weather' in locals():
                print("Input data:")
                print(current_weather)
            if 'current_data' in locals():
                print("\nProcessed data:")
                print(current_data.head())
            return None

    def load_models(self):
        """Load models with better error handling"""
        try:
            print(f"\nLoading models from: {self.model_path}")
            
            # Check if models exist
            required_files = [
                'temperature_model.joblib',
                'humidity_model.joblib',
                'pressure_model.joblib',
                'wind_speed_model.joblib',
                'scaler.joblib'
            ]
            
            missing_files = []
            for file in required_files:
                file_path = os.path.join(self.model_path, file)
                if not os.path.exists(file_path):
                    missing_files.append(file)
                else:
                    print(f"Found: {file}")
            
            if missing_files:
                print(f"\nMissing model files: {missing_files}")
                print("Training new models...")
                return self.train(['Mumbai', 'London', 'New York'])  # Train with default cities
            
            # Load models
            for target in self.target_variables:
                model_path = os.path.join(self.model_path, f'{target}_model.joblib')
                self.models[target] = joblib.load(model_path)
                print(f"Loaded model: {target}")
            
            # Load scaler
            scaler_path = os.path.join(self.model_path, 'scaler.joblib')
            self.scaler = joblib.load(scaler_path)
            print("Loaded scaler")
            
            return True
            
        except Exception as e:
            print(f"Error loading models: {str(e)}")
            print("Full error details:", traceback.format_exc())
            return False

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