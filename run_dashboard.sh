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
source entorno_virtual/Scripts/activate

# Step 4: Install required libraries
echo "Installing required libraries..."
pip install -r requirements.txt

# Step 5: Run the Streamlit app
echo "Launching the Streamlit app..."
streamlit run Ventas.py
