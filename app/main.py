import streamlit as st
from config import APP_TITLE, validate_config

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
    Welcome to the **Streamlit & LangChain AI Application Template**! 
    
    This boilerplate template is fully structured to help you scale AI workflows easily.
    """)
    
    # Configuration Validation Alerts
    warnings = validate_config()
    if warnings:
        with st.expander("⚠️ Configuration Alerts", expanded=True):
            for warning in warnings:
                st.warning(warning)
                
    st.divider()
    
    # Features List
    st.header("⚡ Features Included")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠️ Technical Architecture")
        st.markdown("""
        - **LangChain Integration**: Built-in folder structure (`models`, `chains`, `prompts`, `handlers`, `utils`).
        - **Dependency Management**: Powered by modern Python developer tooling `pyproject.toml` and `uv` lock files.
        - **Robust Configuration**: Centralized environment variable settings (`config.py`).
        - **Custom Callbacks**: Real-time token streaming supported out-of-the-box (`stream_handler.py`).
        """)
        
    with col2:
        st.subheader("💡 Streamlit UI Components")
        st.markdown("""
        - **Multi-page Architecture**: Easily add pages under the `pages/` directory.
        - **Global Sidebar Settings**: Dynamic model settings, temperature controls, and token inputs in a shared component.
        - **Native Memory State**: Persistent conversation history storing (`StreamlitChatMessageHistory`).
        """)

    st.divider()
    
    # Next steps for developers
    st.header("👉 How to Get Started")
    st.markdown("""
    1. Click on the **Chat Assistant** page in the sidebar navigation to try the LangChain interactive demo.
    2. Provide your API Key in the sidebar or save it in a `.env` file at the root.
    3. Modify this landing page inside `app/main.py`.
    4. Build complex workflows in `app/chains/` using customized system rules in `app/prompts/templates.py`.
    """)

if __name__ == "__main__":
    setup_page()
    render_landing_page()