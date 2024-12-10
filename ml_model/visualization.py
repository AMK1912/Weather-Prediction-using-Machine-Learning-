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
            print("\nCreating combined plot...")
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    '<b>Temperature Forecast (°C)</b>',
                    '<b>Humidity Forecast (%)</b>',
                    '<b>Pressure Trend (hPa)</b>',
                    '<b>Wind Speed Forecast (m/s)</b>'
                ),
                vertical_spacing=0.3,
                horizontal_spacing=0.15,
            )
            
            times = [p['timestamp'] for p in predictions]
            
            # Add traces with improved styling
            traces = [
                ('temperature', 1, 1, '°C', 'Temperature'),
                ('humidity', 1, 2, '%', 'Humidity'),
                ('pressure', 2, 1, 'hPa', 'Pressure'),
                ('wind_speed', 2, 2, 'm/s', 'Wind Speed')
            ]
            
            for param, row, col, unit, title in traces:
                values = [p[param] for p in predictions]
                
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=values,
                        name=title,
                        line=dict(
                            color=self.colors[param],
                            width=3
                        ),
                        mode='lines+markers',
                        marker=dict(
                            size=8,
                            symbol='circle'
                        ),
                        hovertemplate=f'{title}: %{{y:.1f}}{unit}<br>Time: %{{x}}<extra></extra>'
                    ),
                    row=row, col=col
                )

            # Update layout with theme-compatible settings
            fig.update_layout(
                height=800,
                showlegend=False,
                template='plotly',  # Use plotly template for better theme compatibility
                margin=dict(t=60, b=40, l=40, r=40),
                font=dict(size=12),
                # Theme will be set by JavaScript
                paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
                plot_bgcolor='rgba(0,0,0,0)'    # Transparent plot area
            )

            # Update axes with theme-compatible settings
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                tickangle=45,
                # Theme-compatible grid
                gridcolor='rgba(128, 128, 128, 0.2)'
            )

            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                # Theme-compatible grid
                gridcolor='rgba(128, 128, 128, 0.2)',
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor='rgba(128, 128, 128, 0.2)'
            )

            print("Plot created successfully")
            return json.loads(fig.to_json())
            
        except Exception as e:
            print(f"Error creating combined plot: {str(e)}")
            print("Full error details:", traceback.format_exc())
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