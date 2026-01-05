#!/bin/bash

# BALE 2.0 Launcher

# 1. Check for Virtual Environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# 2. Activate
source .venv/bin/activate

# 3. Install Requirements (Quietly)
echo "Checking dependencies..."
pip install -q -r requirements.txt

# 4. Check API Keys
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your real API Keys."
    exit 1
fi

# 5. Run Streamlit
echo "Starting BALE 2.0..."
streamlit run app.py
