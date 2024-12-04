#!/bin/bash

# Step 1: Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python and try again."
    exit 1
fi

# Step 2: Check if the virtual environment exists
if [ ! -d "entorno_virtual" ]; then
    echo "The virtual environment 'entorno_virtual' does not exist. Please create it manually."
    exit 1
fi

# Step 3: Activate the virtual environment
echo "Activating the virtual environment..."
# Check if we're using Git Bash (or similar terminal in Windows)
if [ -f "entorno_virtual/Scripts/activate" ]; then
    # For Git Bash (or Bash shell on Windows)
    source entorno_virtual/Scripts/activate
elif [ -f "entorno_virtual/Scripts/activate.bat" ]; then
    # For CMD
    echo "Please run the script in a compatible terminal (CMD or PowerShell)."
    exit 1
else
    echo "Unable to activate the virtual environment. Ensure you are in the correct directory."
    exit 1
fi

# Verify if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
else
    echo "Virtual environment activation failed."
    exit 1
fi

# Step 4: Install required libraries
echo "Installing required libraries..."
pip install -r requirements.txt

# Step 5: Run the Streamlit app
echo "Launching the Streamlit app..."
python -m streamlit run Ventas.py