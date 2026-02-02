#!/bin/bash
# Start the monitoring server
# Run this script to start the central server

echo "========================================"
echo "Starting Monitoring Server"
echo "========================================"
echo

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Check if config.py exists
if [ ! -f config.py ]; then
    echo "WARNING: config.py not found"
    echo "Copying from config.example.py..."
    cp config.example.py config.py
    echo
    echo "IMPORTANT: Edit config.py to set your API_TOKEN and STORAGE_ROOT"
    echo
    read -p "Press enter to continue..."
fi

echo "Starting server..."
echo "Press Ctrl+C to stop"
echo

python3 main.py
