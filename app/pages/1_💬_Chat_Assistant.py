import sys
import os
import streamlit as st

# Add the parent app directory to sys.path to resolve internal imports
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if app_dir not in sys.path:
    sys.path.append(app_dir)

from components.chat import render_chat_page

if __name__ == "__main__":
    st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")
    render_chat_page()
