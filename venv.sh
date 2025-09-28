#!/bin/bash
# Virtual environment activation script for Unix/Linux/Mac
# Usage: source venv.sh

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated!"
    echo ""
    echo "To deactivate, run: deactivate"
else
    echo "Virtual environment not found!"
    echo "Please run: python -m venv venv"
fi
