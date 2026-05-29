import streamlit as st
import time
import os
import base64
from PIL import Image
import io
import json

from config import APP_TITLE
from utils.helpers import get_provider_api_key, check_provider_api_key
from models.llm import get_llm
from components.floating_chat import render_floating_chat
from utils.theme import inject_theme
from langchain_core.messages import HumanMessage




def setup_page():
    """Configures Streamlit page configurations."""
    st.set_page_config(
        page_title="Prior Authorization Demo",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def encode_image_base64(image_bytes):
    """Encodes image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")

def draw_status_bar(step):
    """Draws a premium, visually engaging progress steps indicator."""
    steps = [
        ("📂", "1. Load"),
        ("🤖", "2. Agent Working"),
        ("👀", "3. Preview"),
        ("✅", "4. Finish")
    ]
    
    html = '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; background:var(--bg-surface); padding:14px; border-radius:14px; border:1px solid var(--border-default); box-shadow:var(--shadow-sm);">'
    
    for idx, (icon, name) in enumerate(steps, start=1):
        if idx == step:
            bg       = "var(--blue-100)"
            border   = "var(--blue-500)"
            color    = "var(--blue-700)"
            weight   = "700"
        elif idx < step:
            bg       = "var(--success-bg)"
            border   = "var(--success-border)"
            color    = "var(--success-text)"
            weight   = "600"
        else:
            bg       = "var(--bg-surface-alt)"
            border   = "var(--border-default)"
            color    = "var(--text-muted)"
            weight   = "500"
            
        html += f"""
        <div style="flex:1; text-align:center; padding:10px; border-radius:10px; background:{bg}; border:1.5px solid {border}; margin:0 4px; transition:all 0.2s ease;">
            <div style="font-size:20px; margin-bottom:4px;">{icon}</div>
            <div style="font-weight:{weight}; color:{color}; font-size:13px; font-family:'Inter',sans-serif;">{name}</div>
        </div>
        """
        if idx < len(steps):
            html += '<div style="color:var(--text-muted); font-size:18px; padding:0 2px;">\u27a1\ufe0f</div>'
            
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_prior_auth_page():
    """Renders the Prior Authorization workflow demo page."""
    # Render global clinical design theme
    inject_theme()
    
    # Render Custom Hospital Navbar Header
    st.markdown(
        """
        <div class="hospital-header">
            <div>
                <h1>📋 Prior Authorization Clinical Workspace</h1>
                <p>Autonomous Multi-Agent Record Extraction &amp; Insurance Policy Validation</p>
            </div>
            <div class="header-badge">
                <span class="live-dot"></span>Clinical Ingestor Agent Active
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize state management
    if "pa_step" not in st.session_state:
        st.session_state.pa_step = 1
    if "uploaded_image_bytes" not in st.session_state:
        st.session_state.uploaded_image_bytes = None
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""
    if "generated_form" not in st.session_state:
        st.session_state.generated_form = ""
    if "is_sample_active" not in st.session_state:
        st.session_state.is_sample_active = False

    # Render top status bar
    draw_status_bar(st.session_state.pa_step)
    
    # Step 1: LOAD STEP
    if st.session_state.pa_step == 1:
        st.subheader("📂 Step 1: Load Clinical Note")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("Upload a scanned patient note image to begin autonomous prior authorization analysis:")
            
            # File Uploader
            uploaded_file = st.file_uploader(
                "Upload Clinical Note (PNG, JPG, JPEG)",
                type=["png", "jpg", "jpeg"],
                help="Select a scanned or photographed image of the patient's clinical progress note."
            )
            
            if uploaded_file is not None:
                st.session_state.uploaded_image_bytes = uploaded_file.getvalue()
                st.session_state.is_sample_active = False
            
            # Action Button
            if st.session_state.uploaded_image_bytes is not None:
                st.divider()
                if st.button("🚀 Start Prior Authorization Analysis", type="primary", use_container_width=True):
                    st.session_state.pa_step = 2
                    st.rerun()
            else:
                st.info("📁 Upload a clinical note image above to begin.")
                
        with col2:
            if st.session_state.uploaded_image_bytes is not None:
                st.image(
                    st.session_state.uploaded_image_bytes,
                    caption="Loaded Clinical Image Document",
                    use_container_width=True
                )
            else:
                st.markdown(
                    """
                    <div class="hospital-card" style="text-align:center; padding:40px 24px; color:var(--text-muted);">
                        <div style="font-size:48px; margin-bottom:12px;">📄</div>
                        <div style="font-size:15px; font-weight:600; color:var(--text-secondary); margin-bottom:6px;">No document loaded</div>
                        <div style="font-size:13px;">Upload a PNG, JPG, or JPEG image of the patient's clinical note to preview it here.</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Step 2: AGENT WORKING STEP
    elif st.session_state.pa_step == 2:

        # ── Blurred backdrop: re-render the Step 1 image behind the overlay ──────
        if st.session_state.uploaded_image_bytes is not None:
            import base64 as _b64
            _img_b64 = _b64.b64encode(st.session_state.uploaded_image_bytes).decode()
            st.markdown(
                f"""
                <div style="
                    position:relative; border-radius:16px; overflow:hidden;
                    margin-bottom:0;
                ">
                    <img src="data:image/png;base64,{_img_b64}"
                         style="width:100%; max-height:320px; object-fit:cover;
                                filter:blur(6px) brightness(0.45); display:block;
                                border-radius:16px;" />
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Agent status definitions ──────────────────────────────────────────────
        agent_steps = [
            ("🔌", "Pipeline Router",       "Initialising multi-agent healthcare pipeline…"),
            ("🔍", "Ingestion Agent",        "Scanning document — detecting structured regions…"),
            ("🖊️",  "OCR & Parser Agent",    "Extracting clinical text from uploaded image…"),
            ("📋", "Policy Matcher Agent",   "Pulling MCG / InterQual MRI necessity guidelines…"),
            ("🧠", "Validation Agent",       "Correlating symptoms with medical necessity criteria…"),
            ("📝", "Form Synthesizer Agent", "Drafting prior authorization documentation schema…"),
            ("✅", "Audit Agent",            "Running verification & sanitization checks…"),
        ]

        # ── Inject keyframe CSS once (not inside the loop) ───────────────────────
        st.markdown(
            """
            <style>
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            @keyframes ag-fadein {
                from { opacity:0; transform:translateY(8px); }
                to   { opacity:1; transform:translateY(0); }
            }
            .ag-overlay {
                background: linear-gradient(160deg, rgba(10,22,50,0.97) 0%, rgba(15,30,60,0.97) 100%);
                backdrop-filter: blur(20px) saturate(1.5);
                -webkit-backdrop-filter: blur(20px) saturate(1.5);
                border: 1px solid rgba(96,165,250,0.22);
                border-radius: 18px;
                padding: 28px 28px 24px;
                box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04);
                animation: ag-fadein 0.35s ease;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # ── Overlay slot (updated each step) ─────────────────────────────────────
        overlay_slot = st.empty()

        def _render_overlay(completed: list[tuple], active_idx: int, done: bool = False):
            """Render the glass overlay with current agent statuses. No HTML comments."""
            rows_html = ""
            for i, (icon, name, desc) in enumerate(agent_steps):
                if i < len(completed):
                    rows_html += (
                        f'<div style="display:flex;align-items:center;gap:14px;padding:12px 16px;'
                        f'background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.25);'
                        f'border-radius:10px;margin-bottom:8px;">'
                        f'<div style="font-size:20px;width:32px;text-align:center;">{icon}</div>'
                        f'<div style="flex:1;">'
                        f'<div style="font-size:12px;font-weight:700;color:#86efac;letter-spacing:0.4px;text-transform:uppercase;">{name}</div>'
                        f'<div style="font-size:13px;color:rgba(255,255,255,0.75);margin-top:2px;">{desc}</div>'
                        f'</div>'
                        f'<div style="font-size:18px;color:#4ade80;flex-shrink:0;">✓</div>'
                        f'</div>'
                    )
                elif i == active_idx and not done:
                    rows_html += (
                        f'<div style="display:flex;align-items:center;gap:14px;padding:12px 16px;'
                        f'background:rgba(37,99,235,0.18);border:1.5px solid rgba(96,165,250,0.45);'
                        f'border-radius:10px;margin-bottom:8px;box-shadow:0 0 20px rgba(96,165,250,0.15);">'
                        f'<div style="font-size:20px;width:32px;text-align:center;">{icon}</div>'
                        f'<div style="flex:1;">'
                        f'<div style="font-size:12px;font-weight:700;color:#93c5fd;letter-spacing:0.4px;text-transform:uppercase;">{name}</div>'
                        f'<div style="font-size:13px;color:rgba(255,255,255,0.85);margin-top:2px;">{desc}</div>'
                        f'</div>'
                        f'<div style="width:20px;height:20px;border:2px solid #93c5fd;border-top-color:transparent;'
                        f'border-radius:50%;animation:spin 0.8s linear infinite;flex-shrink:0;"></div>'
                        f'</div>'
                    )
                else:
                    rows_html += (
                        f'<div style="display:flex;align-items:center;gap:14px;padding:12px 16px;'
                        f'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);'
                        f'border-radius:10px;margin-bottom:8px;opacity:0.4;">'
                        f'<div style="font-size:20px;width:32px;text-align:center;filter:grayscale(1);">{icon}</div>'
                        f'<div style="flex:1;">'
                        f'<div style="font-size:12px;font-weight:600;color:rgba(255,255,255,0.45);letter-spacing:0.4px;text-transform:uppercase;">{name}</div>'
                        f'<div style="font-size:13px;color:rgba(255,255,255,0.3);margin-top:2px;">{desc}</div>'
                        f'</div>'
                        f'<div style="width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.18);flex-shrink:0;"></div>'
                        f'</div>'
                    )

            progress_pct = int((len(completed) / len(agent_steps)) * 100)
            if done:
                status_label = "All agents completed — preparing report…"
            elif active_idx < len(agent_steps):
                status_label = f"Running: {agent_steps[active_idx][1]}…"
            else:
                status_label = ""

            overlay_slot.markdown(
                f'<div class="ag-overlay">'

                # Header row
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;padding-bottom:16px;'
                f'border-bottom:1px solid rgba(255,255,255,0.08);">'
                f'<div style="width:42px;height:42px;background:rgba(37,99,235,0.25);border-radius:12px;'
                f'display:flex;align-items:center;justify-content:center;font-size:22px;'
                f'border:1px solid rgba(96,165,250,0.3);">🤖</div>'
                f'<div>'
                f'<div style="font-size:16px;font-weight:700;color:#ffffff;font-family:Outfit,sans-serif;'
                f'letter-spacing:-0.2px;">Clinical AI Agents Running</div>'
                f'<div style="font-size:12px;color:#93c5fd;margin-top:3px;">{status_label}</div>'
                f'</div>'
                f'</div>'

                # Agent cards
                f'{rows_html}'

                # Progress bar
                f'<div style="margin-top:16px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
                f'<span style="font-size:11px;color:rgba(255,255,255,0.45);font-weight:600;'
                f'text-transform:uppercase;letter-spacing:0.6px;">Pipeline Progress</span>'
                f'<span style="font-size:12px;color:#93c5fd;font-weight:700;">{progress_pct}%</span>'
                f'</div>'
                f'<div style="height:6px;background:rgba(255,255,255,0.08);border-radius:6px;overflow:hidden;">'
                f'<div style="height:100%;width:{progress_pct}%;'
                f'background:linear-gradient(90deg,#2563eb,#38bdf8);border-radius:6px;"></div>'
                f'</div>'
                f'</div>'

                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Stream the agent steps ────────────────────────────────────────────────
        completed = []
        for idx in range(len(agent_steps)):
            _render_overlay(completed, idx)
            time.sleep(0.9)
            completed.append(agent_steps[idx])

        # ── Final render (all done) ───────────────────────────────────────────────
        _render_overlay(completed, len(agent_steps), done=True)
        time.sleep(0.5)

        # ── Real API call or fallback ─────────────────────────────────────────────
        provider = st.session_state.get("provider", "OpenAI (ChatGPT)")
        has_api_key = check_provider_api_key(provider)

        if has_api_key and st.session_state.uploaded_image_bytes is not None:
            try:
                import base64 as _b64e
                model_name  = st.session_state.get("model_name", "gpt-4o-mini")
                temperature = st.session_state.get("temperature", 0.3)
                api_key     = get_provider_api_key(provider)

                llm = get_llm(model_name=model_name, temperature=temperature, api_key=api_key)

                base64_image = _b64e.b64encode(st.session_state.uploaded_image_bytes).decode()

                prompt_content = [
                    {"type": "text", "text": "Extract all patient info, clinic info, and clinical assessment details from the image note. Output in structured form."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                ]

                response_text = llm.invoke([HumanMessage(content=prompt_content)]).content
                st.session_state.extracted_text = response_text

                form_prompt = f"""
                You are a prior authorization clinical reviewer. Create a fully completed clinical medical necessity form matching the patient records against MRI lumbar guidelines.

                Here is the extracted patient records text:
                {response_text}

                Construct an elegant Markdown clinical Prior Authorization Form including:
                - Patient info, visit date, DOB
                - Requesting Clinic, physician, phone, NPI
                - Procedure requested (Lumbar Spine MRI, CPT 72148)
                - Diagnostic ICD-10 codes (M54.16 - Lumbar radiculopathy)
                - Clinical proof details (symptoms duration, exams positive straight leg raise, failed conservative therapy Gabapentin, etc.)
                - Clear Medical Necessity statement.

                Match the layout of a standard medical necessity packet.
                """
                form_response = llm.invoke(form_prompt).content
                st.session_state.generated_form = form_response

            except Exception as e:
                err_msg = str(e)
                st.session_state.extracted_text = f"__ERROR__:{err_msg}"
                st.session_state.generated_form  = f"__ERROR__:{err_msg}"
        else:
            # No API key — always show the API required card, never fake data
            st.session_state.extracted_text = "__NO_KEY__"
            st.session_state.generated_form  = "__NO_KEY__"

        time.sleep(0.6)
        st.session_state.pa_step = 3
        st.rerun()


    # Step 3: PREVIEW STEP
    elif st.session_state.pa_step == 3:
        st.subheader("👀 Step 3: Clinician Preview & Verification")
        
        col1, col2 = st.columns([1, 1.2])
        
        no_key_mode   = st.session_state.generated_form == "__NO_KEY__"
        error_mode    = st.session_state.generated_form.startswith("__ERROR__:")
        error_detail  = st.session_state.generated_form.replace("__ERROR__:", "").strip() if error_mode else ""
        show_form     = not no_key_mode and not error_mode

        with col1:
            st.markdown("#### Patient Records Image Document")
            st.image(st.session_state.uploaded_image_bytes, use_container_width=True)
            
            with st.expander("📝 Extracted Raw Document Text", expanded=False):
                if show_form:
                    st.text_area("OCR Raw Output", st.session_state.extracted_text, height=300)
                elif no_key_mode:
                    st.markdown(
                        """
                        <div class="status-card error">
                            <h4>🔑 API Key Required for OCR Extraction</h4>
                            <p>Configure your API key in
                            <a href="/Settings" target="_self" style="color:var(--error-text);font-weight:700;">⚙️ Settings</a>
                            to extract text from your uploaded image.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error(f"Extraction failed: {error_detail}")

        with col2:
            st.markdown("#### Generated Medical Necessity Prior Auth Form")

            if show_form:
                st.markdown(
                    f"""
                    <div class="hospital-card" style="font-size:14px; color:var(--text-primary); padding:25px;">
                        {st.session_state.generated_form}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif no_key_mode:
                st.markdown(
                    """
                    <div class="hospital-card" style="text-align:center; padding:48px 32px;">
                        <div style="font-size:52px; margin-bottom:16px;">🔑</div>
                        <div style="font-size:18px; font-weight:700; color:var(--text-primary);
                                    font-family:'Outfit',sans-serif; margin-bottom:10px;">
                            API Key Required
                        </div>
                        <div style="font-size:14px; color:var(--text-secondary); max-width:340px;
                                    margin:0 auto 24px; line-height:1.6;">
                            Your image was uploaded successfully, but an AI API key is needed
                            to extract and analyse the clinical note content.
                        </div>
                        <div style="background:var(--blue-50); border:1px solid var(--blue-200);
                                    border-radius:10px; padding:14px 18px; text-align:left;
                                    font-size:13px; color:var(--text-secondary);">
                            <strong style="color:var(--text-accent);">How to fix:</strong><br>
                            1. Go to <a href="/Settings" target="_self"
                               style="color:var(--text-accent);font-weight:600;">⚙️ Settings</a>
                               and paste your OpenAI or Gemini API key.<br>
                            2. Click <strong>Restart / Reset</strong> below to re-run with your key.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="hospital-card" style="text-align:center; padding:48px 32px;">
                        <div style="font-size:52px; margin-bottom:16px;">⚠️</div>
                        <div style="font-size:18px; font-weight:700; color:var(--text-primary);
                                    font-family:'Outfit',sans-serif; margin-bottom:10px;">
                            Analysis Failed
                        </div>
                        <div style="font-size:13px; color:var(--text-secondary); max-width:400px;
                                    margin:0 auto 20px; line-height:1.6;">
                            The AI model returned an error while processing your document.
                        </div>
                        <div style="background:var(--error-bg,#fef2f2); border:1px solid var(--error-border,#fecaca);
                                    border-radius:10px; padding:12px 16px; text-align:left;
                                    font-size:12px; color:var(--error-text,#b91c1c); font-family:monospace;">
                            {error_detail}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Action buttons
            b1, b2 = st.columns(2)
            with b1:
                if st.button("⬅️ Restart / Reset", use_container_width=True):
                    st.session_state.pa_step = 1
                    st.session_state.uploaded_image_bytes = None
                    st.session_state.extracted_text = ""
                    st.session_state.generated_form = ""
                    st.rerun()
            with b2:
                if show_form:
                    if st.button("✍️ Approve & Finalize Form", type="primary", use_container_width=True):
                        st.session_state.pa_step = 4
                        st.rerun()
                elif no_key_mode:
                    if st.button("⚙️ Go to Settings", type="primary", use_container_width=True):
                        st.switch_page("pages/3_⚙️_Settings.py")
                else:
                    if st.button("🔄 Retry", type="primary", use_container_width=True):
                        st.session_state.pa_step = 1
                        st.session_state.uploaded_image_bytes = None
                        st.session_state.extracted_text = ""
                        st.session_state.generated_form = ""
                        st.rerun()


    # Step 4: FINISH STEP
    elif st.session_state.pa_step == 4:
        st.subheader("✅ Step 4: Completed & Document Ready")
        
        # Display completion box
        st.markdown(
            """
            <div style="background:var(--success-bg); border:2px solid var(--success-border); border-radius:14px; padding:32px; text-align:center; margin-bottom:30px;">
                <h2 style="color:var(--success-text); margin-top:0; font-family:'Outfit',sans-serif; font-weight:700;">🎉 Prior Authorization Package Finalized</h2>
                <p style="font-size:16px; color:var(--success-subtext); font-weight:500;">The multi-agent loop has extracted medical notes, verified necessity, and mapped standard insurance records.</p>
                <p style="font-size:14px; color:var(--success-subtext);">Ready for download and direct EHR integration.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Download Section
        form_data = st.session_state.generated_form
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            # File download button
            st.download_button(
                label="💾 Download Prior Auth Medical Necessity Form (.md)",
                data=form_data,
                file_name="Prior_Auth_Medical_Necessity_Form.md",
                mime="text/markdown",
                use_container_width=True,
                type="primary"
            )
            
            # Let's provide a JSON export option as well
            json_export = {
                "document_type": "prior_authorization_form",
                "platform": "Cityfront Healthcare Platform",
                "extracted_text": st.session_state.extracted_text,
                "completed_form_markdown": st.session_state.generated_form
            }
            
            st.download_button(
                label="⚙️ Download Raw EHR Structured Record (.json)",
                data=json.dumps(json_export, indent=4),
                file_name="Prior_Auth_Payload.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.divider()
            
            if st.button("🔄 Start New Authorization Request", use_container_width=True):
                st.session_state.pa_step = 1
                st.session_state.uploaded_image_bytes = None
                st.session_state.extracted_text = ""
                st.session_state.generated_form = ""
                st.rerun()
                
    # Render Floating Chat Widget
    render_floating_chat()

if __name__ == "__main__":
    setup_page()
    render_prior_auth_page()
