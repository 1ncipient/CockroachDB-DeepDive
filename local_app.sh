#!/bin/bash

# Set environment variables
export FLASK_APP=application.py
export FLASK_DEBUG=1
export FLASK_ENV=local

# Run the Flask application
python3 -m flask run -h localhost -p 8048
