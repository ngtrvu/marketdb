#!/bin/bash
mkdir -p /cloudsql/stagvn:asia-southeast1:stagvn-pg/

# Apply database migrations
echo "Apply database migrations"
python3 manage.py migrate

# Start server
echo "Starting server"
gunicorn marketdb.wsgi:application --bind=0.0.0.0:8000 --workers=3 --timeout=90 --log-level=debug
