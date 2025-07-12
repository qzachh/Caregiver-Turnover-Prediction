#!/bin/bash

echo "Starting WeCare247 Churn Prediction Automation..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python3 and try again"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if required packages are installed
echo "Checking required packages..."
if ! python3 -c "import requests, pandas, sklearn" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install required packages"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo
echo "Running automation..."
echo

# Run the main automation script
python3 main.py

read -p "Press Enter to exit..."
