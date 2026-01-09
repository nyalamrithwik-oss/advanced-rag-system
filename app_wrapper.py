"""
Alternative Streamlit Entry Point

This is the recommended way to run the Streamlit app. Place this file in 
the project root and run:

    streamlit run app_wrapper.py

Or from PowerShell (with environment activated):

    & .\.venv\Scripts\Activate.ps1
    streamlit run app_wrapper.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path for proper module imports
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main app
if __name__ == "__main__":
    # This imports from the src package using relative imports
    from src.app import main
    main()
