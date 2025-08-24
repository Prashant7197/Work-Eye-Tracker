#!/bin/bash
# Wellness at Work - Eye Tracker Launcher for macOS/Linux

echo "Starting Wellness at Work - Eye Tracker..."

# Check if virtual environment exists
if [ ! -f ".venv/bin/python" ]; then
    echo "Virtual environment not found. Setting up..."
    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
fi

# Launch the application
.venv/bin/python main.py
