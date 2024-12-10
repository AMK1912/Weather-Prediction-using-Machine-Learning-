from ml_model.weather_predictor import Weather_Prediction
import os
import pandas as pd
from time import sleep

def verify_feature_order(predictor):
    """
    Verify feature order consistency
    """
    print("\nVerifying feature order...")
    
    # Get test data
    test_city = "London"
    current = predictor.data_collector.get_current_weather(test_city)
    
    if not current:
        print("Could not get test data")
        return False
    
    # Try prediction
    predictions = predictor.predict(current, hours=1)
    
    if predictions:
        print("Feature order verification successful")
        print("\nSample prediction:")
        for key, value in predictions[0].items():
            print(f"{key}: {value}")
        return True
    else:
        print("Feature order verification failed")
        return False

def test_predictions(predictor, city):
    """
    Test predictions for a single city
    """
    print(f"\nTesting predictions for {city}...")
    
    try:
        # Get current weather
        current = predictor.data_collector.get_current_weather(city)
        if not current:
            print(f"Could not get current weather for {city}")
            return False
            
        print(f"Current temperature in {city}: {current['temperature']}°C")
        
        # Make predictions
        predictions = predictor.predict(current, hours=24)
        if not predictions:
            print(f"Could not generate predictions for {city}")
            return False
            
        # Show sample predictions
        print("\nSample predictions:")
        for i, pred in enumerate(predictions[:3]):  # Show first 3 predictions
            print(f"Hour {i+1}: {pred['temperature']}°C")
            
        return True
        
    except Exception as e:
        print(f"Error testing {city}: {e}")
        return False

def train_weather_models():
    print("Starting model training...")
    
    try:
        predictor = Weather_Prediction()
        
        # Test cities
        cities = [
            "Mumbai", "Delhi", "London", "New York", "Tokyo",
            "Dubai", "Singapore", "Paris", "Berlin", "Sydney"
        ]
        
        print(f"\nTraining with {len(cities)} cities...")
        
        # Collect training data
        all_data = []
        for city in cities:
            print(f"\nCollecting data for {city}...")
            current = predictor.data_collector.get_current_weather(city)
            if current:
                current['city'] = city
                all_data.append(pd.DataFrame([current]))
            
            forecast = predictor.data_collector.get_3hour_forecast(city)
            if forecast:
                forecast_df = pd.DataFrame(forecast)
                forecast_df['city'] = city
                all_data.append(forecast_df)
        
        if not all_data:
            print("No data collected!")
            return
        
        # Combine all data
        training_data = pd.concat(all_data, ignore_index=True)
        
        # Save raw training data
        predictor.save_training_data(training_data, cities)
        
        # Train models
        success = predictor.train(cities)
        
        if success:
            print("\nModels trained successfully!")
            
            # Test predictions
            test_cities = ["Mumbai", "London", "New York"]
            print("\nTesting predictions...")
            
            for city in test_cities:
                print(f"\nTesting {city}...")
                current = predictor.data_collector.get_current_weather(city)
                if current:
                    predictions = predictor.predict(current, hours=24)
                    if predictions:
                        print(f"[PASS] {city} predictions successful")
                        # Save predictions
                        predictor.save_predictions(city, predictions)
                    else:
                        print(f"[FAIL] {city} predictions failed")
                else:
                    print(f"[FAIL] Could not get current weather for {city}")
        else:
            print("\nError training models!")
            
    except Exception as e:
        print(f"Error in training script: {e}")

if __name__ == "__main__":
    # Set console encoding to UTF-8
    import sys
    import os
    if sys.platform.startswith('win'):
        if sys.stdout.encoding != 'utf-8':
            os.system('chcp 65001')  # Set Windows console to UTF-8
    
    train_weather_models() 