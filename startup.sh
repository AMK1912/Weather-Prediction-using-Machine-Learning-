#!/bin/bash
echo "Starting deployment setup..."

# Create necessary directories
mkdir -p models
mkdir -p data
mkdir -p predictions

# Train models
echo "Training models..."
python train_models.py

# Start the application
echo "Starting application..."
gunicorn --workers=4 --threads=4 --timeout 120 --bind 0.0.0.0:$PORT 'app:create_app()' 
