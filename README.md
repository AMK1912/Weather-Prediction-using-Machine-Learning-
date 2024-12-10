# Weather Prediction Web Application

This project is a web application that predicts weather conditions using machine learning models. It provides interactive visualizations and supports light/dark mode themes. The application is deployed on Render.

## Features

- **Weather Predictions**: Provides 24-hour forecasts for temperature, humidity, pressure, and wind speed.
- **Interactive Visualizations**: Uses Plotly to display interactive charts for weather trends.
- **Light/Dark Mode**: Users can switch between light and dark themes.
- **Responsive Design**: The application is mobile-friendly and adapts to different screen sizes.

## Technologies Used

- **Flask**: Web framework for building the application.
- **Gunicorn**: WSGI HTTP server for running the app in production.
- **Plotly**: Library for creating interactive visualizations.
- **Pandas**: Data manipulation and analysis.
- **Scikit-learn**: Machine learning library for training models.
- **Render**: Platform for deploying the application.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/weather-prediction.git
   cd weather-prediction
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Train the models**:
   ```bash
   python train_models.py
   ```

5. **Run the application**:
   ```bash
   flask run
   ```

## Deployment

The application is deployed on Render. To deploy:

1. **Create a `render.yaml`** with the necessary configuration.
2. **Push your code to GitHub**.
3. **Connect your repository to Render** and set the build and start commands.

## Usage

- Visit the deployed application URL.
- Enter a city name to get weather predictions.
- Use the theme switcher to toggle between light and dark modes.
- Explore the interactive visualizations for detailed weather trends.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## Acknowledgments

- Thanks to the open-source community for providing the tools and libraries used in this project.
- Special thanks to [Your Name] for guidance and support.
