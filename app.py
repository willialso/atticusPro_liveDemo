"""
Production entry point for Render deployment
"""
import streamlit as st
import os
import sys

# Ensure proper port binding for Render
port = int(os.environ.get("PORT", 8501))

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run
try:
    from demo_frontend import main
    
    if __name__ == "__main__":
        # For Render deployment
        main()
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please check that demo_frontend.py exists in the same directory")
