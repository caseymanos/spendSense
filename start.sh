#!/bin/bash
# Railway start script that routes to correct service based on SERVICE_TYPE env var

if [ "$SERVICE_TYPE" = "operator" ]; then
    echo "Starting operator dashboard..."
    exec python ui/app_operator_nicegui.py
else
    echo "Starting backend API..."
    echo "Initializing database and data..."
    python scripts/initialize_railway.py
    echo "Starting uvicorn server..."
    exec uvicorn api.main:app --host 0.0.0.0 --port $PORT
fi
