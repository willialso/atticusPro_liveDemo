import streamlit as st
import os
import sys

# Set up the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the main demo
from demo_frontend import main

if __name__ == "__main__":
    main()
