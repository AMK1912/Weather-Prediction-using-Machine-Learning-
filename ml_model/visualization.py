import plotly.graph_objects as go
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
            line=dict(color=self.colors['temperature'], width=3)
        ))
        
        fig.update_layout(
            title='Temperature Forecast',
            xaxis_title='Time',
            yaxis_title='Temperature (°C)',
            height=400,
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
            line=dict(color=self.colors['humidity'], width=3)
        ))
        
        fig.update_layout(
            title='Humidity Forecast',
            xaxis_title='Time',
            yaxis_title='Humidity (%)',
            height=400,
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
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '<b>Temperature Forecast</b>',
                '<b>Humidity Forecast</b>',
                '<b>Pressure Trend</b>',
                '<b>Wind Speed Forecast</b>'
            ),
            vertical_spacing=0.35,
            horizontal_spacing=0.25,
            row_heights=[0.5, 0.5]
        )
        
        times = [p['timestamp'] for p in predictions]
        
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['temperature'] for p in predictions],
                name='Temperature',
                line=dict(color=self.colors['temperature'], width=2.5)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['humidity'] for p in predictions],
                name='Humidity',
                line=dict(color=self.colors['humidity'], width=2.5)
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['pressure'] for p in predictions],
                name='Pressure',
                line=dict(color=self.colors['pressure'], width=2.5)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=times,
                y=[p['wind_speed'] for p in predictions],
                name='Wind Speed',
                line=dict(color=self.colors['wind'], width=2.5)
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=1000,
            width=1200,
            showlegend=False,
            template='plotly_white',
            margin=dict(t=120, b=80, l=80, r=80),
            grid=dict(rows=2, columns=2, pattern='independent'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=20),
            font=dict(size=14)
        )

        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_xaxes(
                    row=i, 
                    col=j,
                    automargin=True,
                    tickangle=45,
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='lightgrey',
                    title=dict(
                        text="Time",
                        standoff=20
                    )
                )
                fig.update_yaxes(
                    row=i,
                    col=j,
                    automargin=True,
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    gridcolor='lightgrey',
                    title=dict(
                        standoff=20
                    )
                )

        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Humidity (%)", row=1, col=2)
        fig.update_yaxes(title_text="Pressure (hPa)", row=2, col=1)
        fig.update_yaxes(title_text="Wind Speed (m/s)", row=2, col=2)

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