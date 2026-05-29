import streamlit as st
import time
import os
from utils.helpers import check_provider_api_key, get_provider_api_key, get_key_source
from utils.theme import inject_theme

def setup_page():
    """Configures the Settings page settings."""
    st.set_page_config(
        page_title="Settings - Cityfront Healthcare",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_settings_page():
    """Renders a premium clinical Settings page."""
    inject_theme()
    
    # Render Custom Hospital Navbar Header
    st.markdown(
        """
        <div class="hospital-header">
            <div>
                <h1>⚙️ Global Agent Configurations</h1>
                <p>Configure API credentials, active model providers, and customize temperature parameters globally</p>
            </div>
            <div class="header-badge">
                <span class="live-dot"></span>Settings Engine Active
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🛠️ Provider & Model Parameters")
        
        # Provider Selector
        provider = st.selectbox(
            "Select AI Provider",
            options=["OpenAI (ChatGPT)", "DeepSeek", "Google Gemini"],
            index=["OpenAI (ChatGPT)", "DeepSeek", "Google Gemini"].index(
                st.session_state.get("provider", "OpenAI (ChatGPT)")
            ) if st.session_state.get("provider") in ["OpenAI (ChatGPT)", "DeepSeek", "Google Gemini"] else 0,
            help="Choose the model provider you want to use."
        )
        
        # Dynamic API Key Input
        p_lower = provider.lower()
        if "openai" in p_lower:
            key_name = "openai_api_key"
            label = "OpenAI API Key"
        elif "deepseek" in p_lower:
            key_name = "deepseek_api_key"
            label = "DeepSeek API Key"
        else:
            key_name = "gemini_api_key"
            label = "Google Gemini API Key"
            
        api_key = st.text_input(
            label,
            type="password",
            placeholder="Paste your key here...",
            help=f"Optionally provide your {label}. If configured in `.env`, you can leave this empty.",
            value=st.session_state.get(key_name, "")
        )
        
        # Dynamic Model Selection
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
            default_val = st.session_state.get("model_name", "gpt-4o-mini")
            default_idx = model_options.index(default_val) if default_val in model_options else 0
        elif provider == "DeepSeek":
            model_options = [
                "deepseek-chat",
                "deepseek-reasoner"
            ]
            default_val = st.session_state.get("model_name", "deepseek-chat")
            default_idx = model_options.index(default_val) if default_val in model_options else 0
        elif provider == "Google Gemini":
            model_options = [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.0-flash",
                "gemini-2.0-pro-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash-exp"
            ]
            default_val = st.session_state.get("model_name", "gemini-2.5-flash")
            default_idx = model_options.index(default_val) if default_val in model_options else 0
            
        model_name = st.selectbox(
            "Model Name",
            options=model_options,
            index=default_idx,
            help=f"Select the Chat model from {provider}."
        )
        
        # Temperature Slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.get("temperature", 0.7),
            step=0.1,
            help="Controls creativity. Lower is more deterministic, higher is more creative."
        )
        
        st.divider()
        
        # Apply Configurations
        if st.button("Apply & Save Configurations", type="primary", use_container_width=True):
            st.session_state.provider = provider
            st.session_state[key_name] = api_key
            st.session_state.model_name = model_name
            st.session_state.temperature = temperature
            
            st.success("⚙️ Global Configurations Saved Successfully!")
            time.sleep(0.6)
            st.rerun()
            
    with col2:
        st.subheader("🔒 Active Connection Status")

        has_key = check_provider_api_key(provider)

        if has_key:
            active_key = get_provider_api_key(provider)
            key_source = get_key_source(provider)
            # Mask: show first 6 + bullets + last 4
            if len(active_key) > 10:
                masked = active_key[:6] + "•" * 20 + active_key[-4:]
            else:
                masked = "•" * 24

            st.markdown(
                f"""
                <div class="status-card success">
                    <h4>🟢 Securely Connected</h4>
                    <p>API credentials for <strong>{provider}</strong> are active and ready.</p>
                    <hr />
                    <ul>
                        <li><strong>Provider:</strong> {provider}</li>
                        <li><strong>Active Model:</strong> <code>{model_name}</code></li>
                        <li><strong>Temperature:</strong> <code>{temperature}</code></li>
                        <li><strong>Key Source:</strong> {key_source}</li>
                        <li><strong>Key (masked):</strong> <code>{masked}</code></li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Determine what env var name to show in the hint
            env_hints = {
                "OpenAI (ChatGPT)": "OPENAI_API_KEY=sk-...",
                "DeepSeek":         "DEEPSEEK_API_KEY=sk-...",
                "Google Gemini":     "GEMINI_API_KEY=AIza...",
            }
            env_hint = env_hints.get(provider, "YOUR_API_KEY=...")

            st.markdown(
                f"""
                <div class="status-card error">
                    <h4>🔴 Credentials Missing or Invalid</h4>
                    <p>No valid API key found for <strong>{provider}</strong>.
                    Placeholders like <code>your_openai_api_key_here</code> are not accepted.</p>
                    <hr />
                    <ul>
                        <li><strong>Option A — Paste above:</strong>
                            Enter your real {label} in the field on the left and click
                            <em>Apply &amp; Save</em>.</li>
                        <li><strong>Option B — Backend .env:</strong>
                            Add <code>{env_hint}</code> to your <code>.env</code> file and restart.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        st.subheader("💡 Tips")
        st.markdown(
            """
            *   **Global Access**: Settings apply to the Prior Authorization pipeline, Chat Assistant, and the floating co-pilot.
            *   **Multimodal**: For analyzing patient note images, use **Gemini** or **GPT-4o** models.
            *   **Security**: Keys pasted in the UI are stored in the browser session only — they are never persisted to disk.
            *   **Valid key formats**: OpenAI & DeepSeek keys start with `sk-`. Gemini keys start with `AIza`.
            """
        )

if __name__ == "__main__":
    setup_page()
    render_settings_page()
