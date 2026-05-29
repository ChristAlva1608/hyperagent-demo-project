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

def check_google_api_key():
    """Verify if Google API Key is present in session state or env."""
    if "google_api_key" in st.session_state and st.session_state.google_api_key:
        return True
    if os.getenv("GOOGLE_API_KEY"):
        return True
    return False

def get_google_api_key():
    """Gets Google API key from session state or env."""
    if "google_api_key" in st.session_state and st.session_state.google_api_key:
        return st.session_state.google_api_key
    return os.getenv("GOOGLE_API_KEY")

def get_provider(model_name: str) -> str:
    """Helper to detect provider based on the model name."""
    from config import SUPPORTED_MODELS
    for provider, models in SUPPORTED_MODELS.items():
        if model_name in models:
            return provider
    return "openai"  # Fallback provider

def check_api_key(model_name: str) -> bool:
    """Verify if the API Key for the model's provider is present."""
    provider = get_provider(model_name)
    if provider == "google":
        return check_google_api_key()
    return check_openai_api_key()

def get_api_key(model_name: str) -> str:
    """Gets the API Key for the model's provider."""
    provider = get_provider(model_name)
    if provider == "google":
        return get_google_api_key()
    return get_openai_api_key()

def clear_chat_history():
    """Clear chat messages in the session state."""
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]