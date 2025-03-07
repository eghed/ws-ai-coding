#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Verify activation
echo "Virtual environment activated. Python path: $(which python)"

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "Creating empty requirements.txt..."
    touch requirements.txt
fi

# Install dependencies if requirements.txt exists and has content
if [ -s "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

echo "Setup complete! Virtual environment is ready to use." 