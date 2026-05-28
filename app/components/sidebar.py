import streamlit as st
from config import DEFAULT_MODEL
from utils.helpers import clear_chat_history

def render_sidebar():
    """Renders the sidebar with configuration options."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # API Key Section
        st.subheader("API Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Provide your OpenAI API Key. If set in .env, you can leave this empty.",
            value=st.session_state.get("api_key", "")
        )
        if api_key:
            st.session_state.api_key = api_key
            
        st.divider()
        
        # Model Parameters
        st.subheader("Model Configuration")
        model_name = st.selectbox(
            "Model Name",
            options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0,
            help="Select the OpenAI Chat model to use."
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