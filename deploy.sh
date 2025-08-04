#!/bin/bash

# Data Automation Bot - Production Deployment Script

set -e

echo "Starting Data Automation Bot deployment..."

# Create necessary directories
mkdir -p logs
mkdir -p reports

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations/setup
echo "Setting up database..."
python -c "
from database.db_manager import DatabaseManager
db = DatabaseManager()
db.initialize_database()
print('Database initialized successfully')
"

# Start the application with Gunicorn
echo "Starting application with Gunicorn..."
exec gunicorn --config gunicorn.conf.py "web.app:create_app()"