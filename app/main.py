import streamlit as st
from config import APP_TITLE, validate_config
from components.floating_chat import render_floating_chat

def setup_page():
    """Configures the main Streamlit page settings."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_landing_page():
    """Renders the landing page content."""
    st.title(f"🚀 {APP_TITLE}")
    st.markdown("""
    Welcome to the **Cityfront Healthcare & AI Agentic Infrastructure Platform**! 
    
    This platform orchestrates deep, stateful, and secure AI agents to automate clinical administrative tasks and medical necessity workflows.
    """)
    
    # Configuration Validation Alerts
    warnings = validate_config()
    if warnings:
        with st.expander("⚠️ Configuration Alerts", expanded=True):
            for warning in warnings:
                st.warning(warning)
                
    st.divider()
    
    # Demo Sections
    st.header("⚡ Active Agentic Demos")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Autonomous Prior Authorization")
        st.markdown("""
        Extract patient clinical charts directly from scans or handwritten notes and verify clinical necessity against insurance guidelines.
        
        *   **Multi-Agent Workflow**: Sequential execution of OCR, Clinical Ingestion, Policy Comparison, and Form Synthesizer agents.
        *   **4-Step Pipeline**: Visual flow tracking through `Load`, `Agent Working`, `Preview`, and `Finish`.
        *   **Interactive Outputs**: Instant Markdown and JSON data package downloads.
        
        👉 **Go to "Prior Authorization" in the sidebar navigation.**
        """)
        
    with col2:
        st.subheader("💬 General Chat Assistant")
        st.markdown("""
        Interact with an underlying conversational assistant backed by LangChain's flexible chain definitions.
        
        *   **Real-time Streaming**: Instant callback handling for token streaming.
        *   **EHR Context Integration**: Chat state persisted via native memory blocks.
        *   **Dynamic Configurations**: Live temperature adjustments.
        
        👉 **Go to "Chat Assistant" in the sidebar navigation.**
        """)

    st.divider()
    
    # Platform Architecture Overview
    st.header("🛠️ Systems & Infrastructure")
    st.markdown("""
    This application boilerplate demonstrates:
    1.  **LangChain Integration**: Built-in architecture covering `models`, `chains`, `prompts`, and `handlers`.
    2.  **Multi-Page Routing**: Native modular pages under the `app/pages/` directory.
    3.  **Modern Python Tooling**: Robust dependency resolution and environment setup powered by `pyproject.toml` and `uv`.
    """)
    
    # Render Floating Chat Widget
    render_floating_chat()

if __name__ == "__main__":
    setup_page()
    render_landing_page()