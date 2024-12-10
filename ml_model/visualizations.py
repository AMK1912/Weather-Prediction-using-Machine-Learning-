import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

def create_comparison_plots(api_forecast, ml_predictions, city):
    """
    Create interactive plots comparing API forecast with ML predictions
    """
    # Convert predictions to DataFrame
    ml_df = pd.DataFrame(ml_predictions)
    ml_df['timestamp'] = pd.to_datetime(ml_df['timestamp'])
    
    # Convert API forecast to DataFrame
    api_df = pd.DataFrame(api_forecast)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature (°C)', 'Humidity (%)', 
                       'Pressure (hPa)', 'Wind Speed (m/s)'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Add traces for each metric
    metrics = {
        'temperature': {'row': 1, 'col': 1, 'color': 'red'},
        'humidity': {'row': 1, 'col': 2, 'color': 'blue'},
        'pressure': {'row': 2, 'col': 1, 'color': 'green'},
        'wind_speed': {'row': 2, 'col': 2, 'color': 'purple'}
    }
    
    for metric, params in metrics.items():
        # API forecast line
        fig.add_trace(
            go.Scatter(
                x=api_df['timestamp'],
                y=api_df[metric],
                name=f'API {metric}',
                line=dict(color=params['color'], dash='solid'),
                opacity=0.7
            ),
            row=params['row'],
            col=params['col']
        )
        
        # ML predictions line
        fig.add_trace(
            go.Scatter(
                x=ml_df['timestamp'],
                y=ml_df[metric],
                name=f'ML {metric}',
                line=dict(color=params['color'], dash='dot'),
                opacity=0.7
            ),
            row=params['row'],
            col=params['col']
        )
    
    # Update layout
    fig.update_layout(
        title=f'Weather Forecast Comparison for {city}',
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_xaxes(title_text="Time", row=2, col=2)
    
    return fig

def create_accuracy_plot(evaluation_results):
    """
    Create plot showing prediction accuracy metrics
    """
    metrics = list(evaluation_results.keys())
    mse_values = [evaluation_results[m]['mse'] for m in metrics]
    rmse_values = [evaluation_results[m]['rmse'] for m in metrics]
    
    fig = go.Figure(data=[
        go.Bar(name='MSE', x=metrics, y=mse_values),
        go.Bar(name='RMSE', x=metrics, y=rmse_values)
    ])
    
    fig.update_layout(
        title='Prediction Accuracy Metrics',
        barmode='group',
        xaxis_title='Weather Metrics',
        yaxis_title='Error Value',
        showlegend=True
    )
    
    return fig

def create_forecast_dashboard(current_weather, api_forecast, ml_predictions, evaluation):
    """
    Create a comprehensive dashboard with all visualizations
    """
    # Create comparison plots
    comparison_fig = create_comparison_plots(api_forecast, ml_predictions, current_weather['city'])
    
    # Create accuracy plot
    accuracy_fig = create_accuracy_plot(evaluation)
    
    return {
        'comparison_plot': comparison_fig.to_json(),
        'accuracy_plot': accuracy_fig.to_json()
    } 