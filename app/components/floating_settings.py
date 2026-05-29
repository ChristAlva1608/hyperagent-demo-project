import streamlit as st
from utils.api_key_validator import check_provider_api_key

def render_floating_settings():
    """Renders an adaptive floating settings FAB above the chat button."""
    
    st.markdown(
        """
        <style>
        /* ============================================================
           SETTINGS FAB — positioned above the chat FAB
        ============================================================ */
        .settings-anchor {
            display: none !important;
        }

        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] {
            position: fixed !important;
            bottom: 105px !important;
            right: 30px !important;
            width: 60px !important;
            height: 60px !important;
            z-index: 999998 !important;
            background: transparent !important;
            border: none !important;
        }

        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"][open],
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"]:has(details[open]),
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"]:has([open]) {
            width: 320px !important;
            height: 360px !important;
        }

        /* Settings FAB trigger button */
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > button,
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > summary,
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > details > summary,
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > details > button {
            position: absolute !important;
            bottom: 0 !important;
            right: 0 !important;
            left: auto !important;
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #334155 0%, #1e293b 100%) !important;
            color: #ffffff !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 22px !important;
            box-shadow: 0 4px 16px rgba(51,65,85,0.45), 0 2px 6px rgba(0,0,0,0.2) !important;
            border: 2px solid rgba(255,255,255,0.12) !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            padding: 0 !important;
            margin: 0 !important;
            outline: none !important;
        }

        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > button:hover,
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > summary:hover,
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > details > summary:hover {
            transform: scale(1.1) translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(51,65,85,0.6), 0 4px 10px rgba(0,0,0,0.25) !important;
            outline: none !important;
        }

        /* Hide chevrons inside FAB */
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > button span:nth-child(2),
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > button [data-testid="stIcon"],
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"] > button svg {
            display: none !important;
        }

        /* Hide body when closed */
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"]:not([open]):not(:has(details[open])):not(:has([open])) [data-testid="stPopoverBody"] {
            display: none !important;
        }

        /* Popover panel — adaptive to dark/light */
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"][open] [data-testid="stPopoverBody"],
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"]:has(details[open]) [data-testid="stPopoverBody"],
        div.element-container:has(.settings-anchor) + div.element-container [data-testid="stPopover"]:has([open]) [data-testid="stPopoverBody"] {
            position: absolute !important;
            bottom: 72px !important;
            right: 0 !important;
            left: auto !important;
            top: auto !important;
            transform: none !important;
            width: 320px !important;
            max-height: 300px !important;
            border-radius: 14px !important;
            border: 1px solid var(--border-default) !important;
            background-color: var(--bg-surface) !important;
            box-shadow: 0 16px 48px rgba(0,0,0,0.18), 0 6px 16px rgba(0,0,0,0.1) !important;
            z-index: 1000000 !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
            animation: slideUpFade 0.22s cubic-bezier(0.4,0,0.2,1) both !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='settings-anchor'></div>", unsafe_allow_html=True)

    with st.popover("⚙️"):
        # Header
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,#1e293b 0%,#334155 100%); padding:14px 18px; margin:-8px -8px 0 -8px; border-radius:12px 12px 0 0;">
                <div style="font-size:15px; font-weight:700; color:#ffffff; font-family:'Outfit',sans-serif;">⚙️ Quick Settings</div>
                <div style="font-size:11px; color:#94a3b8; margin-top:2px;">Active configuration snapshot</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        
        # Active config display
        provider    = st.session_state.get("provider",    "OpenAI (ChatGPT)")
        model_name  = st.session_state.get("model_name", "gpt-4o-mini")
        temperature = st.session_state.get("temperature", 0.7)
        has_key     = check_provider_api_key(provider)
        
        conn_badge_class = "badge-green" if has_key else "badge-red"
        conn_label       = "🟢 Connected"  if has_key else "🔴 No Credentials"
        
        st.markdown(
            f"""
            <div style="padding:0 4px;">
                <div style="margin-bottom:10px; display:flex; align-items:center; justify-content:space-between;">
                    <span style="font-size:12px; font-weight:600; color:var(--text-secondary);">Status</span>
                    <span class="badge {conn_badge_class}">{conn_label}</span>
                </div>
                <div style="background:var(--bg-surface-alt); border:1px solid var(--border-default); border-radius:8px; padding:12px; margin-bottom:10px;">
                    <div style="font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Active Configuration</div>
                    <div style="font-size:13px; color:var(--text-primary); margin-bottom:4px;">🤖 <strong>Provider:</strong> {provider}</div>
                    <div style="font-size:13px; color:var(--text-primary); margin-bottom:4px;">🔮 <strong>Model:</strong> <code style="background:var(--blue-50);color:var(--text-accent);padding:1px 5px;border-radius:3px;">{model_name}</code></div>
                    <div style="font-size:13px; color:var(--text-primary);">🌡 <strong>Temperature:</strong> <code style="background:var(--blue-50);color:var(--text-accent);padding:1px 5px;border-radius:3px;">{temperature}</code></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("🔧 Open Full Settings", type="primary", use_container_width=True):
            st.switch_page("pages/3_⚙️_Settings.py")
