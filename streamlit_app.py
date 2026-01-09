"""
Streamlit App Wrapper

This script properly initializes the Python path and runs the Streamlit app.
It should be called from the project root:
    streamlit run streamlit_app.py

or from PowerShell:
    python -m streamlit run streamlit_app.py

This avoids module import issues by ensuring the project root is in sys.path.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import and run the app
from src.app import main

if __name__ == "__main__":
    main()
