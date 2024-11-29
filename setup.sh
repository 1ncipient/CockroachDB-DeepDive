#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Install uv in the virtual environment
./venv/bin/python -m pip install uv

# Run 'uv clean'
./venv/bin/python -m uv clean

# Upgrade pip
./venv/bin/python -m uv pip install --upgrade pip

# Install wheel
./venv/bin/python -m uv pip install wheel

# Install dependencies from requirements.txt
./venv/bin/python -m uv pip install -r requirements.txt

# Activate the virtual environment
source ./venv/bin/activate
