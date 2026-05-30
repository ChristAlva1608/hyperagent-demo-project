"""
Cityfront Healthcare Streamlit App Package
Exposes core packages and automatically initializes global configuration and logging.
"""

import os
import sys

# Dynamically add path offsets to sys.path to guarantee robust module resolution
# across varying execution environments (Streamlit, Pytest, manual runs).
_app_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_app_dir = os.path.dirname(os.path.abspath(__file__))

if _app_parent not in sys.path:
    sys.path.insert(0, _app_parent)
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

# Initialize application-wide logging and environment configuration
import config