import streamlit as st
import os

def check_openai_api_key():
    """Verify if OpenAI API Key is present in session state or env."""
    if "api_key" in st.session_state and st.session_state.api_key:
        return True
    if os.getenv("OPENAI_API_KEY"):
        return True
    return False

def get_openai_api_key():
    """Gets OpenAI API key from session state or env."""
    if "api_key" in st.session_state and st.session_state.api_key:
        return st.session_state.api_key
    return os.getenv("OPENAI_API_KEY")

def clear_chat_history():
    """Clear chat messages in the session state."""
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]