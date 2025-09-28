#!/usr/bin/env python3
"""
GIF-Tools Desktop Application Launcher

Simple launcher script for the GIF-Tools desktop GUI application.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the main application
from desktop_app.main import main

if __name__ == "__main__":
    main()
