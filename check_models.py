import os
from ml_model.weather_predictor import Weather_Prediction

def check_models():
    predictor = Weather_Prediction()
    model_path = predictor.model_path
    
    print(f"\nChecking models in: {model_path}")
    
    if not os.path.exists(model_path):
        print("Models directory does not exist!")
        return False
    
    required_files = [
        'temperature_model.joblib',
        'humidity_model.joblib',
        'pressure_model.joblib',
        'wind_speed_model.joblib',
        'scaler.joblib'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        else:
            size = os.path.getsize(file_path) / 1024  # Size in KB
            print(f"Found {file} ({size:.2f} KB)")
    
    if missing_files:
        print("\nMissing model files:")
        for file in missing_files:
            print(f"- {file}")
        return False
    
    print("\nAll required models are present!")
    return True

if __name__ == "__main__":
    if check_models():
        print("\nSystem is ready for predictions!")
    else:
        print("\nPlease train the models first using:")
        print("python train_models.py") 