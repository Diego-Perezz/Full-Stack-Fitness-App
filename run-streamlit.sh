# # !/usr/bin/env bash

# docker build -t streamlit-app .

# docker run -p 8080:8080 streamlit-app


#!/bin/bash

# Check if we're running in Cloud Run
if [ -n "$PORT" ]; then
    # Cloud Run deployment
    echo "Running in Cloud Run on port $PORT"
    streamlit run --server.port=$PORT --server.address=0.0.0.0 app.py
else
    # Local development with Docker
    echo "Running locally with Docker"
    docker build -t streamlit-app .
    docker run -p 8080:8080 streamlit-app
fi