import streamlit as st
import time
from utils.helpers import get_provider_api_key, check_provider_api_key
from chains.chat_chain import get_conversational_chain
from langchain_core.messages import HumanMessage, AIMessage

def render_floating_chat():
    """Renders a premium adaptive floating chat co-pilot widget (bottom-right FAB)."""
    
    st.markdown(
        """
        <style>
        /* ============================================================
           FLOATING CHAT — FAB Container
        ============================================================ */
        [data-testid="stPopover"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            width: 60px !important;
            height: 60px !important;
            z-index: 999999 !important;
            background: transparent !important;
            border: none !important;
        }

        /* Expand when open */
        [data-testid="stPopover"][open],
        [data-testid="stPopover"]:has(details[open]),
        [data-testid="stPopover"]:has([open]) {
            width: 400px !important;
            height: 640px !important;
        }

        /* FAB trigger button — circular pill */
        [data-testid="stPopover"] > button,
        [data-testid="stPopover"] > summary,
        [data-testid="stPopover"] > details > summary,
        [data-testid="stPopover"] > details > button {
            position: absolute !important;
            bottom: 0 !important;
            right: 0 !important;
            left: auto !important;
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important;
            color: #ffffff !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 22px !important;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.45), 0 2px 8px rgba(0,0,0,0.15) !important;
            border: 2px solid rgba(255,255,255,0.2) !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            padding: 0 !important;
            margin: 0 !important;
            outline: none !important;
        }

        /* Hide WebKit details marker */
        [data-testid="stPopover"] > summary::-webkit-details-marker,
        [data-testid="stPopover"] details > summary::-webkit-details-marker {
            display: none !important;
        }

        /* Hide chevron icon / second span / SVGs inside the FAB button */
        [data-testid="stPopover"] > button span:nth-child(2),
        [data-testid="stPopover"] > button [data-testid="stIcon"],
        [data-testid="stPopover"] > summary [data-testid="stIcon"],
        [data-testid="stPopover"] > details > summary [data-testid="stIcon"],
        [data-testid="stPopover"] > button svg,
        [data-testid="stPopover"] > summary svg,
        [data-testid="stPopover"] > details > summary svg {
            display: none !important;
        }

        /* FAB hover */
        [data-testid="stPopover"] > button:hover,
        [data-testid="stPopover"] > summary:hover,
        [data-testid="stPopover"] > details > summary:hover {
            transform: scale(1.1) translateY(-2px) !important;
            box-shadow: 0 8px 28px rgba(37, 99, 235, 0.6), 0 4px 12px rgba(0,0,0,0.2) !important;
            outline: none !important;
        }

        /* Hide body when closed */
        [data-testid="stPopover"]:not([open]):not(:has(details[open])):not(:has([open])) [data-testid="stPopoverBody"] {
            display: none !important;
        }

        /* Popover panel — emerges above FAB */
        [data-testid="stPopover"][open] [data-testid="stPopoverBody"],
        [data-testid="stPopover"]:has(details[open]) [data-testid="stPopoverBody"],
        [data-testid="stPopover"]:has([open]) [data-testid="stPopoverBody"] {
            position: absolute !important;
            bottom: 72px !important;
            right: 0 !important;
            left: auto !important;
            top: auto !important;
            transform: none !important;
            width: 400px !important;
            max-height: 560px !important;
            border-radius: 16px !important;
            border: 1px solid var(--border-default) !important;
            background-color: var(--bg-surface) !important;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2), 0 8px 20px rgba(0,0,0,0.12) !important;
            z-index: 1000000 !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
            animation: slideUpFade 0.25s cubic-bezier(0.4,0,0.2,1) both !important;
        }

        @keyframes slideUpFade {
            from { opacity: 0; transform: translateY(12px) scale(0.97); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* Scrollbar inside chat history */
        .floating-chat-box::-webkit-scrollbar { width: 4px; }
        .floating-chat-box::-webkit-scrollbar-track { background: transparent; }
        .floating-chat-box::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 4px; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize chat history
    if "floating_chat_history" not in st.session_state:
        st.session_state.floating_chat_history = [
            AIMessage(content="Hello! I'm your Clinical Co-Pilot. I can help analyze medical necessity guidelines, draft prior auth requests, or review patient charts.")
        ]
    
    with st.popover("💬"):
        # ── Header ──────────────────────────────────────────────
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%); padding:16px 20px; margin:-8px -8px 0 -8px; border-radius:14px 14px 0 0;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:38px; height:38px; background:rgba(255,255,255,0.12); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:18px; border:1px solid rgba(255,255,255,0.15);">🤖</div>
                    <div>
                        <div style="font-size:15px; font-weight:700; color:#ffffff; font-family:'Outfit',sans-serif; letter-spacing:-0.2px;">Clinical Co-Pilot</div>
                        <div style="font-size:11px; color:#93c5fd; font-weight:500; display:flex; align-items:center; gap:5px;">
                            <span style="width:6px;height:6px;background:#22c55e;border-radius:50%;display:inline-block;animation:pulse-dot 1.8s ease infinite;"></span>
                            AI-Powered Healthcare Assistant
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ── Quick Suggestions ────────────────────────────────────
        st.markdown(
            """
            <p style="font-size:10px; font-weight:700; color:var(--text-muted); letter-spacing:0.8px; text-transform:uppercase; margin:14px 0 8px 0;">Quick Actions</p>
            """,
            unsafe_allow_html=True
        )
        
        suggestions = [
            ("📋 MRI Guidelines", "What are the clinical guidelines required to approve a Lumbar Spine MRI (CPT 72148)?"),
            ("✍️ Draft PA Appeal", "Draft a prior authorization appeal for patient John Doe whose Lumbar MRI was denied due to lack of documented PT."),
            ("🔍 CPT 72148 Rules", "What clinical indicators must be met for CPT code 72148 (Lumbar MRI)?")
        ]
        
        selected_prompt = None
        sug_cols = st.columns(len(suggestions))
        for col, (label, prompt_text) in zip(sug_cols, suggestions):
            with col:
                if st.button(label, key=f"f_sug_{label[:8]}", use_container_width=True):
                    selected_prompt = prompt_text
        
        st.divider()
        
        # ── Chat History ─────────────────────────────────────────
        chat_html = "<div class='floating-chat-box' style='height:170px;max-height:170px;overflow-y:auto;padding-right:4px;margin-bottom:12px;'>"
        for msg in st.session_state.floating_chat_history:
            if msg.type == "ai":
                bg_color   = "var(--blue-50)"
                border_clr = "var(--blue-300)"
                label_str  = "🤖 Co-Pilot"
                label_color = "var(--text-accent)"
            else:
                bg_color   = "var(--bg-surface-alt)"
                border_clr = "var(--border-default)"
                label_str  = "👤 You"
                label_color = "var(--text-secondary)"
            
            content = msg.content.replace('\n', '<br>')
            chat_html += (
                f'<div style="background:{bg_color};border-left:3px solid {border_clr};'
                f'padding:10px 12px;border-radius:6px;margin-bottom:8px;font-size:13px;'
                f'line-height:1.45;color:var(--text-primary);">'
                f'<div style="font-weight:700;font-size:10px;color:{label_color};'
                f'letter-spacing:0.5px;text-transform:uppercase;margin-bottom:5px;">{label_str}</div>'
                f'{content}</div>'
            )
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # ── Input & Send ─────────────────────────────────────────
        provider = st.session_state.get("provider", "OpenAI (ChatGPT)")
        has_api_key = check_provider_api_key(provider)
        
        user_text = st.text_input(
            "Message",
            key="f_chat_input_text",
            placeholder="Ask about guidelines, policies, or patient care...",
            label_visibility="collapsed"
        )
        
        c1, c2 = st.columns([3, 1])
        with c1:
            send_btn = st.button("Send →", key="f_chat_send_button", type="primary", use_container_width=True)
        with c2:
            clear_btn = st.button("Clear", key="f_chat_clear_button", use_container_width=True)
        
        if not has_api_key:
            st.markdown(
                "<p style='font-size:11px;color:var(--warning-text);background:var(--warning-bg);"
                "border:1px solid var(--warning-border);border-radius:6px;padding:7px 10px;margin-top:6px;'>"
                "⚠️ Configure API key in <a href='/Settings' target='_self' style='color:inherit;font-weight:700;'>Settings</a> for live AI responses.</p>",
                unsafe_allow_html=True
            )
        
        # ── Clear Logic ──────────────────────────────────────────
        if clear_btn:
            st.session_state.floating_chat_history = [
                AIMessage(content="Hello! I'm your Clinical Co-Pilot. How can I assist you today?")
            ]
            st.rerun()
        
        # ── Send Logic ───────────────────────────────────────────
        exec_prompt = None
        if send_btn and user_text:
            exec_prompt = user_text
        elif selected_prompt:
            exec_prompt = selected_prompt
        
        if exec_prompt:
            st.session_state.floating_chat_history.append(HumanMessage(content=exec_prompt))
            
            if has_api_key:
                try:
                    model_name  = st.session_state.get("model_name", "gpt-4o-mini")
                    temperature = st.session_state.get("temperature", 0.7)
                    api_key     = get_provider_api_key(provider)
                    chain = get_conversational_chain(model_name=model_name, temperature=temperature, api_key=api_key)
                    response = chain.invoke({"input": exec_prompt, "history": st.session_state.floating_chat_history[:-1]})
                    st.session_state.floating_chat_history.append(AIMessage(content=response))
                except Exception as e:
                    st.session_state.floating_chat_history.append(
                        AIMessage(content=f"⚠️ Error: {str(e)}")
                    )
            else:
                time.sleep(0.5)
                mock_answers = {
                    "What are the clinical guidelines required to approve a Lumbar Spine MRI (CPT 72148)?":
                        "According to MCG (Milliman) for Lumbar MRI (CPT 72148), approval requires:\n"
                        "1. Documented lumbar radiculopathy / stenosis suspicion AND\n"
                        "2. ≥6 weeks conservative therapy failure (PT, NSAIDs) OR\n"
                        "3. Red-flag findings: cauda equina, progressive motor loss, malignancy.",
                    "What clinical indicators must be met for CPT code 72148 (Lumbar MRI)?":
                        "CPT 72148 (Lumbar MRI without contrast) requires:\n"
                        "• Low back pain radiating along a dermatomal path.\n"
                        "• Positive SLR test or objective neuro deficits.\n"
                        "• Failed conservative treatment (PT + pharmacological trial).",
                }
                response = mock_answers.get(exec_prompt,
                    "I've reviewed your query. For live clinical analysis, configure your API key in Settings. "
                    "In demo mode, I can confirm this matches standard healthcare compliance guidelines.")
                st.session_state.floating_chat_history.append(AIMessage(content=response))
            
            st.rerun()
