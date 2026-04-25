#!/bin/bash

echo "====================================="
echo "PIPELINE CREATOR - DATABASE SETUP"
echo "====================================="
echo "This script prepares the database and"
echo "optionally loads initial example data"
echo "====================================="
echo

# Move to script directory (IMPORTANT for double click)
cd "$(dirname "$0")"

# --- Python check ---
echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found. Please install Python 3"
    read -p "Press Enter to exit..."
    exit 1
fi

# --- virtual environment ---
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

echo "Activating virtual environment..."
source venv/bin/activate

# --- install dependencies ---
echo "Installing required dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn streamlit sqlalchemy

# --- reset DB ---
echo
echo "Preparing database..."

if [ -f "PIPELINE_CREATOR_DB.db" ]; then
    echo "Existing database found"
    echo "Deleting database..."
    rm PIPELINE_CREATOR_DB.db
else
    echo "No existing database found"
fi

# --- create DB ---
echo
echo "Creating database structure..."
python3 -m DB.CreaDB

# --- user choice ---
echo
read -p "Do you want to populate the database with initial data? (Y/N): " choice

if [[ "$choice" == "Y" || "$choice" == "y" ]]; then
    echo "Populating database..."
    python3 -m DB.ValInizialeDB
    echo "Database successfully populated"
else
    echo "Database left empty"
fi

echo
echo "====================================="
echo "DATABASE SETUP COMPLETED"
echo "====================================="
read -p "Press Enter to exit..."