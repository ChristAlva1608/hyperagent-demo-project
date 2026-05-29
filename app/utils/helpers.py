import streamlit as st
import os

def check_provider_api_key(provider: str) -> bool:
    """Verify if the API Key for the specific provider is present in the backend environment."""
    p_lower = provider.lower()
    
    if "openai" in p_lower:
        if os.getenv("OPENAI_API_KEY"):
            return True
            
    elif "deepseek" in p_lower:
        if os.getenv("DEEPSEEK_API_KEY"):
            return True
            
    elif "gemini" in p_lower or "google" in p_lower:
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            return True
            
    return False

def get_provider_api_key(provider: str) -> str:
    """Gets the API Key for the specific provider from the backend environment."""
    p_lower = provider.lower()
    
    if "openai" in p_lower:
        return os.getenv("OPENAI_API_KEY", "")
        
    elif "deepseek" in p_lower:
        return os.getenv("DEEPSEEK_API_KEY", "")
        
    elif "gemini" in p_lower or "google" in p_lower:
        if os.getenv("GEMINI_API_KEY"):
            return os.getenv("GEMINI_API_KEY")
        return os.getenv("GOOGLE_API_KEY", "")
        
    return ""

def check_openai_api_key():
    """Verify if OpenAI API Key is present in session state or env."""
    return check_provider_api_key("openai")

def get_openai_api_key():
    """Gets OpenAI API key from session state or env."""
    return get_provider_api_key("openai")

def clear_chat_history():
    """Clear chat messages in the session state."""
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]