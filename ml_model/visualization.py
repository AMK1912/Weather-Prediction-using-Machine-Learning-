import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime

class WeatherVisualizer:
    def __init__(self):
        self.colors = {
            'temperature': '#FF6B6B',
            'humidity': '#4ECDC4',
            'pressure': '#45B7D1',
            'wind': '#96CEB4'
        }

    def create_temperature_plot(self, predictions):
        """Create interactive temperature visualization"""
        times = [p['timestamp'] for p in predictions]
        temps = [p['temperature'] for p in predictions]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=temps,
            mode='lines+markers',
            name='Temperature',
            line=dict(color=self.colors['temperature'], width=3),
            hovertemplate='Time: %{x}<br>Temperature: %{y}°C<extra></extra>'
        ))
        
        fig.update_layout(
            title='24-Hour Temperature Forecast',
            xaxis_title='Time',
            yaxis_title='Temperature (°C)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())

    def create_humidity_plot(self, predictions):
        """Create interactive humidity visualization"""
        times = [p['timestamp'] for p in predictions]
        humidity = [p['humidity'] for p in predictions]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=humidity,
            mode='lines+markers',
            name='Humidity',
            fill='tozeroy',
            line=dict(color=self.colors['humidity'], width=3),
            hovertemplate='Time: %{x}<br>Humidity: %{y}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='24-Hour Humidity Forecast',
            xaxis_title='Time',
            yaxis_title='Humidity (%)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())

    def create_pressure_plot(self, predictions):
        """Create interactive pressure visualization"""
        times = [p['timestamp'] for p in predictions]
        pressure = [p['pressure'] for p in predictions]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=pressure,
            mode='lines+markers',
            name='Pressure',
            line=dict(color=self.colors['pressure'], width=3),
            hovertemplate='Time: %{x}<br>Pressure: %{y} hPa<extra></extra>'
        ))
        
        fig.update_layout(
            title='24-Hour Pressure Trend',
            xaxis_title='Time',
            yaxis_title='Pressure (hPa)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())

    def create_wind_plot(self, predictions):
        """Create interactive wind speed visualization"""
        times = [p['timestamp'] for p in predictions]
        wind = [p['wind_speed'] for p in predictions]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=wind,
            mode='lines+markers',
            name='Wind Speed',
            line=dict(color=self.colors['wind'], width=3),
            hovertemplate='Time: %{x}<br>Wind Speed: %{y} m/s<extra></extra>'
        ))
        
        fig.update_layout(
            title='24-Hour Wind Speed Forecast',
            xaxis_title='Time',
            yaxis_title='Wind Speed (m/s)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())

    def create_combined_plot(self, predictions):
        """Create interactive combined visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Temperature Forecast',
                'Humidity Forecast',
                'Pressure Trend',
                'Wind Speed Forecast'
            )
        )
        
        times = [p['timestamp'] for p in predictions]
        
        # Temperature
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['temperature'] for p in predictions],
                name='Temperature',
                line=dict(color=self.colors['temperature'], width=2),
                hovertemplate='Temp: %{y}°C<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Humidity
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['humidity'] for p in predictions],
                name='Humidity',
                line=dict(color=self.colors['humidity'], width=2),
                hovertemplate='Humidity: %{y}%<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Pressure
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['pressure'] for p in predictions],
                name='Pressure',
                line=dict(color=self.colors['pressure'], width=2),
                hovertemplate='Pressure: %{y} hPa<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Wind Speed
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['wind_speed'] for p in predictions],
                name='Wind Speed',
                line=dict(color=self.colors['wind'], width=2),
                hovertemplate='Wind: %{y} m/s<extra></extra>'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return json.loads(fig.to_json())

    def create_all_plots(self, predictions):
        """Create all interactive visualizations"""
        return {
            'temperature': self.create_temperature_plot(predictions),
            'humidity': self.create_humidity_plot(predictions),
            'pressure': self.create_pressure_plot(predictions),
            'wind': self.create_wind_plot(predictions),
            'combined': self.create_combined_plot(predictions)
        } 