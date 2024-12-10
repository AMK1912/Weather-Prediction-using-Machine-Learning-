from flask import Blueprint, render_template, request, jsonify, Response
from ml_model.weather_predictor import Weather_Prediction
from ml_model.data_collector import Weather_Data_Collector
from ml_model.visualizations import create_forecast_dashboard
from ml_model.visualization import WeatherVisualizer
import json
import plotly
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import traceback

main = Blueprint('main', __name__)
weather_predictor = Weather_Prediction()
weather_collector = Weather_Data_Collector()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/get_weather', methods=['POST'])
def get_weather():
    try:
        city = request.form['city'].strip()  # Get city from form input
        
        if not city:
            return jsonify({
                'success': False,
                'error': 'Please enter a city name'
            })
        
        weather_collector = Weather_Data_Collector()
        
        # Get current weather
        current_weather = weather_collector.get_current_weather(city)
        if not current_weather:
            return jsonify({
                'success': False,
                'error': f"Could not find weather data for '{city}'. Please check the city name and try again."
            })
        
        # Get forecast data
        forecast = weather_collector.get_3hour_forecast(city)
        if forecast:
            # Create visualization data
            df = pd.DataFrame(forecast)
            fig = px.line(df, 
                x='timestamp',
                y=['temperature', 'humidity', 'pressure', 'wind_speed'],
                title=f'Weather Forecast for {current_weather["city"]}, {current_weather["country"]}',
                labels={
                    'timestamp': 'Time',
                    'temperature': 'Temperature (°C)',
                    'humidity': 'Humidity (%)',
                    'pressure': 'Pressure (hPa)',
                    'wind_speed': 'Wind Speed (m/s)'
                }
            )
            
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Get daily summary
            daily_forecast = weather_collector.group_forecast_by_day(forecast)
            
            return jsonify({
                'success': True,
                'current_weather': current_weather,
                'hourly_forecast': forecast[:8],  # Next 24 hours
                'daily_forecast': daily_forecast,
                'plot_data': plot_json
            })
        
        return jsonify({
            'success': False,
            'error': 'Unable to fetch forecast data'
        })
        
    except Exception as e:
        print(f"Error in get_weather route: {str(e)}")  # Log the error
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching weather data'
        })

@main.route('/predict', methods=['POST'])
def predict_weather():
    try:
        print("\n=== Starting Weather Prediction ===")
        
        city = request.form['city']
        print(f"Received request for city: {city}")
        
        weather_collector = Weather_Data_Collector()
        weather_predictor = Weather_Prediction()
        
        # Get current weather
        print("Getting current weather...")
        current_weather = weather_collector.get_current_weather(city)
        print(f"Current weather: {current_weather}")
        
        if not current_weather:
            return Response(
                json.dumps({
                    'success': False,
                    'error': f"Could not find weather data for '{city}'"
                }),
                mimetype='application/json'
            )
        
        # Get predictions
        print("Getting predictions...")
        ml_predictions = weather_predictor.predict(current_weather, hours=24)
        print(f"Generated {len(ml_predictions) if ml_predictions else 0} predictions")
        
        if not ml_predictions:
            return Response(
                json.dumps({
                    'success': False,
                    'error': "Could not generate weather predictions"
                }),
                mimetype='application/json'
            )
        
        # Create visualizations
        visualizer = WeatherVisualizer()
        plots = visualizer.create_all_plots(ml_predictions)
        
        # Create response
        response_data = {
            'success': True,
            'city': city,
            'current_weather': current_weather,
            'ml_predictions': ml_predictions,
            'plots': plots
        }
        
        print("Sending response...")
        print(json.dumps(response_data, indent=2, cls=DateTimeEncoder))
        
        return Response(
            json.dumps(response_data, cls=DateTimeEncoder),
            mimetype='application/json'
        )
        
    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            json.dumps({
                'success': False,
                'error': str(e)
            }),
            mimetype='application/json'
        )

@main.route('/train', methods=['POST'])
def train_model():
    try:
        cities = [
            "London", "New York", "Tokyo", "Paris", "Sydney",
            "Berlin", "Moscow", "Dubai", "Singapore", "Mumbai"
        ]
        
        if weather_predictor.train(cities):
            return jsonify({
                'success': True,
                'message': 'Model trained successfully'
            })
        
        return jsonify({
            'success': False,
            'error': 'Unable to train model'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })