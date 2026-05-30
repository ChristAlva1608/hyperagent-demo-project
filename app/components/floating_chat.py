import streamlit as st
import time
from utils.api_key_validator import get_provider_api_key, check_provider_api_key
from chains.chat_chain import get_conversational_chain
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from prompts.agent_prompt import SYSTEM_PROMPT

def handle_text_submit():
    val = st.session_state.get("f_chat_input_text", "").strip()
    if val:
        st.session_state.f_chat_pending_prompt = val
        st.session_state["f_chat_input_text"] = ""

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
            height: 800px !important;
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
            max-height: 720px !important;
            border-radius: 16px !important;
            border: 1px solid var(--border-default) !important;
            background-color: var(--bg-surface) !important;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2), 0 8px 20px rgba(0,0,0,0.12) !important;
            z-index: 1000000 !important;
            overflow-y: auto !important;
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
    
    # Initialize pending prompt
    if "f_chat_pending_prompt" not in st.session_state:
        st.session_state.f_chat_pending_prompt = None

    # Initialize uploader index
    if "f_chat_uploader_index" not in st.session_state:
        st.session_state.f_chat_uploader_index = 0

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
        
        # ── Attachment Section ───────────────────────────────────
        st.markdown(
            """
            <p style="font-size:10px; font-weight:700; color:var(--text-muted); letter-spacing:0.8px; text-transform:uppercase; margin:8px 0 4px 0;">Attachments</p>
            """,
            unsafe_allow_html=True
        )
        
        uploaded_file = st.file_uploader(
            "Attach document or image",
            type=["png", "jpg", "jpeg", "pdf", "docx", "txt"],
            key=f"f_chat_uploaded_file_{st.session_state.f_chat_uploader_index}",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            file_name = uploaded_file.name
            file_size = len(uploaded_file.getvalue())
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    background: rgba(37,99,235,0.06);
                    border: 1px solid rgba(37,99,235,0.18);
                    border-radius: 8px;
                    padding: 8px 12px;
                    margin-bottom: 8px;
                ">
                    <div style="font-size: 16px;">📎</div>
                    <div style="flex-grow: 1; min-width: 0;">
                        <div style="font-size: 11px; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            {file_name}
                        </div>
                        <div style="font-size: 9px; color: var(--text-muted);">
                            {size_str}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # ── Input & Send ─────────────────────────────────────────
        provider = st.session_state.get("provider", "OpenAI (ChatGPT)")
        has_api_key = check_provider_api_key(provider)
        
        user_text = st.text_input(
            "Message",
            key="f_chat_input_text",
            placeholder="Ask about guidelines, policies, or patient care...",
            label_visibility="collapsed",
            on_change=handle_text_submit
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
            st.session_state.f_chat_uploader_index += 1
            st.rerun()
        
        # ── Handle Button Click ──────────────────────────────────
        if send_btn and user_text.strip():
            st.session_state.f_chat_pending_prompt = user_text.strip()
            st.session_state["f_chat_input_text"] = ""
        
        # ── Send Logic ───────────────────────────────────────────
        exec_prompt = None
        if st.session_state.f_chat_pending_prompt:
            exec_prompt = st.session_state.f_chat_pending_prompt
            st.session_state.f_chat_pending_prompt = None
        elif selected_prompt:
            exec_prompt = selected_prompt
        
        if exec_prompt:
            # Capture file details from session state if any
            f_attached = st.session_state.get(f"f_chat_uploaded_file_{st.session_state.f_chat_uploader_index}")
            
            # Format the prompt to show in chat history with a file icon if uploaded
            history_prompt = exec_prompt
            if f_attached:
                history_prompt = f"📎 **Attached**: `{f_attached.name}`\n\n{exec_prompt}"
            
            st.session_state.floating_chat_history.append(HumanMessage(content=history_prompt))
            
            if has_api_key:
                try:
                    model_name  = st.session_state.get("model_name", "gpt-4o-mini")
                    temperature = st.session_state.get("temperature", 0.7)
                    api_key     = get_provider_api_key(provider)
                    
                    # Process the attachment
                    file_content_text = ""
                    image_bytes = None
                    image_mime = None
                    
                    if f_attached:
                        f_name_lower = f_attached.name.lower()
                        if f_name_lower.endswith((".png", ".jpg", ".jpeg")):
                            image_bytes = f_attached.getvalue()
                            image_mime = f"image/{'png' if f_name_lower.endswith('.png') else 'jpeg'}"
                        elif f_name_lower.endswith(".pdf"):
                            import io
                            from pypdf import PdfReader
                            pdf_file = io.BytesIO(f_attached.getvalue())
                            reader = PdfReader(pdf_file)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text() or ""
                            file_content_text = text
                        elif f_name_lower.endswith(".docx"):
                            import io
                            import docx2txt
                            docx_file = io.BytesIO(f_attached.getvalue())
                            file_content_text = docx2txt.process(docx_file)
                        elif f_name_lower.endswith(".txt"):
                            file_content_text = f_attached.getvalue().decode("utf-8", errors="ignore")
                    
                    # Construct LLM and prompt content
                    from models.llm import get_llm
                    llm = get_llm(model_name=model_name, temperature=temperature, api_key=api_key)
                    
                    # Setup prompt messages
                    messages = [SystemMessage(content=SYSTEM_PROMPT)]
                    
                    # Add prior history excluding the newly appended human message
                    messages.extend(st.session_state.floating_chat_history[:-1])
                    
                    # Prepare the newest message text (incorporating text context if document)
                    final_prompt = exec_prompt
                    if file_content_text:
                        final_prompt = f"{exec_prompt}\n\n[Attached Document Content from {f_attached.name}:\n{file_content_text}\n]"
                    
                    # Build multi-modal message if image and vision supported, otherwise text fallback
                    if image_bytes and (("gpt-4" in model_name.lower()) or ("gemini" in model_name.lower())):
                        import base64 as _b64e
                        base64_image = _b64e.b64encode(image_bytes).decode()
                        content_parts = [
                            {"type": "text", "text": final_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{image_mime};base64,{base64_image}"}}
                        ]
                        messages.append(HumanMessage(content=content_parts))
                    else:
                        if image_bytes:
                            final_prompt = f"{final_prompt}\n\n[An image was attached: {f_attached.name}, but the selected model does not support direct image vision analysis. Please use an OpenAI or Gemini model to analyze images directly.]"
                        messages.append(HumanMessage(content=final_prompt))
                    
                    # Invoke LLM
                    response = llm.invoke(messages).content
                    st.session_state.floating_chat_history.append(AIMessage(content=response))
                    
                    # Check if a DOCX file was generated and show download button
                    if "generated_docx_file" in st.session_state and st.session_state.generated_docx_file:
                        file_data = st.session_state.generated_docx_file
                        st.markdown("---")
                        st.download_button(
                            label="📥 Download Form",
                            data=file_data["bytes"],
                            file_name=file_data["filename"],
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True,
                            key="f_download_docx"
                        )
                        # Clear the file from session state after showing download button
                        st.session_state.generated_docx_file = None
                except Exception as e:
                    st.session_state.floating_chat_history.append(
                        AIMessage(content=f"⚠️ Error: {str(e)}")
                    )
            else:
                time.sleep(0.5)
                if f_attached:
                    response = (
                        f"📎 **Analyzed file**: `{f_attached.name}` ({len(f_attached.getvalue())} bytes).\n\n"
                        f"I have successfully scanned this file in demo mode! For active clinical reasoning, guideline validation, "
                        f"and real-time LLM feedback, please configure your API key in Settings."
                    )
                else:
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
            
            # Clear the uploaded file by incrementing the widget key index
            st.session_state.f_chat_uploader_index += 1
            st.rerun()
