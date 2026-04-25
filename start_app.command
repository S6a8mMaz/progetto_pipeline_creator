#!/bin/bash

echo "====================================="
echo "PIPELINE CREATOR - APPLICATION START"
echo "====================================="
echo

# Move to script directory
cd "$(dirname "$0")"

# --- Python check ---
echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found"
    read -p "Press Enter to exit..."
    exit 1
fi

# --- check virtual environment ---
if [ ! -d "venv" ]; then
    echo "ERROR: virtual environment not found"
    echo "Run setup_db.command first"
    read -p "Press Enter to exit..."
    exit 1
fi

# --- activate venv ---
echo "Activating virtual environment..."
source venv/bin/activate

# --- start backend ---
echo "Starting FastAPI backend..."
osascript -e 'tell application "Terminal" to do script "cd \"'"$(pwd)"'\"; source venv/bin/activate; python3 -m uvicorn main:app --reload"'

sleep 3

# --- start frontend ---
echo "Starting Streamlit UI..."
osascript -e 'tell application "Terminal" to do script "cd \"'"$(pwd)"'\"; source venv/bin/activate; python3 -m streamlit run InterfacciaUtente.py"'

echo
echo "====================================="
echo "APPLICATION STARTED"
echo "====================================="
echo "FastAPI:   http://127.0.0.1:8000/docs"
echo "Streamlit: http://localhost:8501"
echo "====================================="

read -p "Press Enter to exit..."