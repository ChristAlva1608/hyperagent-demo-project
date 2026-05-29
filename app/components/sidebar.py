import streamlit as st
from config import DEFAULT_MODEL
from utils.api_key_validator import clear_chat_history, check_provider_api_key

def render_sidebar():
    """Renders the sidebar with dynamic configuration options for multiple AI providers."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Provider Selector
        st.subheader("AI Provider")
        provider = st.selectbox(
            "Select Provider",
            options=["OpenAI (ChatGPT)", "DeepSeek", "Google Gemini"],
            index=0,
            help="Choose the model provider you want to use."
        )
        st.session_state.provider = provider
        
        st.divider()
        
        # Secure Connection Status (Backend Only)
        st.subheader("API Connection Status")
        has_key = check_provider_api_key(provider)
        
        if has_key:
            st.success("🔒 Securely Connected")
            st.caption(f"Credentials for **{provider}** are loaded securely from your backend environment variables.")
        else:
            st.error("⚠️ Credentials Missing")
            st.caption(f"Please configure the API keys for **{provider}** securely inside the server `.env` file.")

        st.divider()
        
        # Dynamic Model Parameters based on provider
        st.subheader("Model Configuration")
        
        if provider == "OpenAI (ChatGPT)":
            model_options = [
                "gpt-4o-mini",
                "gpt-4o",
                "o1-mini",
                "o1-preview",
                "o3-mini",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ]
            default_idx = 0
        elif provider == "DeepSeek":
            model_options = [
                "deepseek-chat",
                "deepseek-reasoner"
            ]
            default_idx = 0
        elif provider == "Google Gemini":
            model_options = [
                "gemini-2.5-flash",
                "gemini-2.5-flash-tts",
                "gemini-2.5-flash-lite",
                "gemini-2.5-pro",
                "gemini-2.0-flash",
                "gemini-2.0-pro-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash-exp"
            ]
            default_idx = 0
            
        model_name = st.selectbox(
            "Model Name",
            options=model_options,
            index=default_idx,
            help=f"Select the Chat model from {provider}."
        )
        st.session_state.model_name = model_name
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controls creativity. Lower is more deterministic, higher is more creative."
        )
        st.session_state.temperature = temperature
        
        st.divider()
        
        # App Info / Reset
        st.subheader("App Actions")
        if st.button("🔄 Reset Chat History", use_container_width=True):
            clear_chat_history()
            st.rerun()
            
        st.divider()
        st.caption("Cityfront Healthcare Platform v0.1.0")