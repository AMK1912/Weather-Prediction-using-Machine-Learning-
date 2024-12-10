import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import traceback

class WeatherVisualizer:
    def __init__(self):
        self.colors = {
            'temperature': '#FF6B6B',
            'humidity': '#4ECDC4',
            'pressure': '#45B7D1',
            'wind_speed': '#96CEB4'
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
            line=dict(color=self.colors['wind_speed'], width=3),
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
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Temperature Forecast (°C)',
                    'Humidity Forecast (%)',
                    'Pressure Trend (hPa)',
                    'Wind Speed Forecast (m/s)'
                ),
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )

            timestamps = [p['timestamp'] for p in predictions]

            # Plot temperature
            values = [p['temperature'] for p in predictions]
            fig.add_trace(
                go.Scatter(x=timestamps, y=values, name='Temperature', line=dict(color='red')),
                row=1, col=1
            )

            # Plot humidity
            values = [p['humidity'] for p in predictions]
            fig.add_trace(
                go.Scatter(x=timestamps, y=values, name='Humidity', line=dict(color='blue')),
                row=1, col=2
            )

            # Plot pressure with enhanced formatting
            values = [p['pressure'] for p in predictions]
            mean_pressure = sum(values) / len(values)
            y_min = mean_pressure - 2  # Reduced range to ±2 hPa
            y_max = mean_pressure + 2
            
            fig.add_trace(
                go.Scatter(
                    x=timestamps, 
                    y=values, 
                    name='Pressure',
                    line=dict(color='green', width=2),
                    mode='lines+markers',  # Add markers to the line
                    marker=dict(size=6)
                ),
                row=2, col=1
            )
            
            # Update pressure subplot
            fig.update_yaxes(
                range=[y_min, y_max],
                tickformat='.1f',
                dtick=0.5,  # Smaller tick interval for more detail
                title_text='Pressure (hPa)',
                row=2, col=1
            )

            # Plot wind speed
            values = [p['wind_speed'] for p in predictions]
            fig.add_trace(
                go.Scatter(x=timestamps, y=values, name='Wind Speed', line=dict(color='purple')),
                row=2, col=2
            )

            # Update layout
            fig.update_layout(
                height=800,
                showlegend=False,
                title_text='Weather Forecast',
                margin=dict(t=60, b=40, l=40, r=40),
            )

            # Update x-axes
            fig.update_xaxes(
                tickangle=45,
                tickformat='%H:%M',  # Show only hours and minutes
                nticks=12,  # Reduce number of x-axis labels
                tickmode='auto',
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGrey'
            )

            # Update y-axes
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGrey',
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor='LightGrey'
            )

            # Add hover template for pressure
            fig.update_traces(
                hovertemplate='<b>Time</b>: %{x}<br><b>Pressure</b>: %{y:.1f} hPa<extra></extra>',
                row=2, col=1
            )

            return json.loads(fig.to_json())

        except Exception as e:
            print(f"Error creating combined plot: {str(e)}")
            traceback.print_exc()
            return None

    def create_all_plots(self, predictions):
        """Create all interactive visualizations"""
        return {
            'temperature': self.create_temperature_plot(predictions),
            'humidity': self.create_humidity_plot(predictions),
            'pressure': self.create_pressure_plot(predictions),
            'wind': self.create_wind_plot(predictions),
            'combined': self.create_combined_plot(predictions)
        } 