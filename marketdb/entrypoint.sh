#!/bin/bash
mkdir -p /cloudsql/stagvn:asia-southeast1:stagvn-pg/

gunicorn marketdb.wsgi:application --bind=0.0.0.0:8000 --workers=3 --timeout=90 --log-level=debug
