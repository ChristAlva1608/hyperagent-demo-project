import streamlit as st
from config import DEFAULT_MODEL, SUPPORTED_MODELS
from utils.helpers import clear_chat_history

def render_sidebar():
    """Renders the sidebar with configuration options."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # API Key Section
        st.subheader("API Configuration")
        
        # Select API Provider
        provider = st.selectbox(
            "API Provider",
            options=["OpenAI", "Google"],
            index=0 if st.session_state.get("provider", "OpenAI") == "OpenAI" else 1,
            help="Choose the API provider to use."
        )
        st.session_state.provider = provider
        
        if provider == "OpenAI":
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                help="Provide your OpenAI API Key. If set in .env, you can leave this empty.",
                value=st.session_state.get("api_key", "")
            )
            if api_key:
                st.session_state.api_key = api_key
        else:
            google_api_key = st.text_input(
                "Google API Key",
                type="password",
                placeholder="AIzaSy...",
                help="Provide your Google API Key. If set in .env, you can leave this empty.",
                value=st.session_state.get("google_api_key", "")
            )
            if google_api_key:
                st.session_state.google_api_key = google_api_key
            
        st.divider()
        
        # Model Parameters
        st.subheader("Model Configuration")
        
        # Get options based on provider
        if provider == "OpenAI":
            model_options = SUPPORTED_MODELS["openai"]
            help_text = "Select the OpenAI Chat model to use."
        else:
            model_options = SUPPORTED_MODELS["google"]
            help_text = "Select the Google Gemini model to use."
            
        current_model = st.session_state.get("model_name")
        default_index = 0
        if current_model in model_options:
            default_index = model_options.index(current_model)
            
        model_name = st.selectbox(
            "Model Name",
            options=model_options,
            index=default_index,
            help=help_text
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
        st.caption("Streamlit-LangChain Template v0.1.0")