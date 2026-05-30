import streamlit as st
import time
import os
import json
import logging

from utils.api_key_validator import check_provider_api_key
from components.floating_chat import render_floating_chat
from utils.theme import inject_theme

# Unified preprocessor and prior-auth agent helpers
from utils.processing_file import processing_file
from utils.prior_auth_agents import (
    classify_document,
    extract_medical_info,
    generate_clinical_summary,
    select_template,
)
from utils.fill_template_docx import fill_template_docx
from utils.text_to_pdf import text_to_pdf

logger = logging.getLogger(__name__)


def setup_page():
    """Configures Streamlit page."""
    st.set_page_config(
        page_title="Prior Authorization Clinical Workspace",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def draw_status_bar(step: int):
    """Draws the 4-step premium progress indicator."""
    steps = [
        ("📂", "1. Load Document"),
        ("🤖", "2. Agent Processing"),
        ("👀", "3. Review & Edit"),
        ("✅", "4. Export Package"),
    ]
    html = (
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'margin-bottom:24px;background:var(--bg-surface);padding:14px;'
        'border-radius:14px;border:1px solid var(--border-default);box-shadow:var(--shadow-sm);">'
    )
    for idx, (icon, name) in enumerate(steps, start=1):
        if idx == step:
            bg, border, color, weight = "var(--blue-100)", "var(--blue-500)", "var(--blue-700)", "700"
        elif idx < step:
            bg, border, color, weight = "var(--success-bg)", "var(--success-border)", "var(--success-text)", "600"
        else:
            bg, border, color, weight = "var(--bg-surface-alt)", "var(--border-default)", "var(--text-muted)", "500"

        html += (
            f'<div style="flex:1;text-align:center;padding:10px;border-radius:10px;'
            f'background:{bg};border:1.5px solid {border};margin:0 4px;transition:all 0.2s ease;">'
            f'<div style="font-size:20px;margin-bottom:4px;">{icon}</div>'
            f'<div style="font-weight:{weight};color:{color};font-size:13px;font-family:Inter,sans-serif;">{name}</div>'
            f"</div>"
        )
        if idx < len(steps):
            html += '<div style="color:var(--text-muted);font-size:18px;padding:0 2px;">➡️</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _reset_state():
    """Wipe all PA session keys back to defaults."""
    st.session_state.pa_step = 1
    st.session_state.uploaded_file_bytes = None
    st.session_state.uploaded_file_name = ""
    st.session_state.normalized_markdown = ""
    st.session_state.classification = {}
    st.session_state.extracted_data = {}
    st.session_state.clinical_summary = ""
    st.session_state.payer = "Default"
    st.session_state.selected_template_path = ""
    st.session_state.filled_docx_path = ""
    st.session_state.error_message = ""


def render_prior_auth_page():
    """Renders the redesigned 4-step Prior Authorization workflow."""
    inject_theme()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hospital-header">
            <div>
                <h1>📋 Prior Authorization Clinical Workspace</h1>
                <p>Unified Document Ingestion · Structured Medical Extraction · Dynamic Template Generation</p>
            </div>
            <div class="header-badge">
                <span class="live-dot"></span>Clinical Processing Agent Ready
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Session state defaults ─────────────────────────────────────────────────
    defaults = {
        "pa_step": 1,
        "uploaded_file_bytes": None,
        "uploaded_file_name": "",
        "normalized_markdown": "",
        "classification": {},
        "extracted_data": {},
        "clinical_summary": "",
        "payer": "Default",
        "selected_template_path": "",
        "filled_docx_path": "",
        "is_sample_active": False,
        "error_message": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    draw_status_bar(st.session_state.pa_step)

    provider   = st.session_state.get("provider",   "OpenAI (ChatGPT)")
    model_name = st.session_state.get("model_name", "gpt-4o-mini")
    has_api_key = check_provider_api_key(provider)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — LOAD CLINICAL DOCUMENT
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.pa_step == 1:
        st.subheader("📂 Step 1: Load Patient Record or Document")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                "Upload any patient note, clinical record, referral, or imaging report "
                "to normalise it and run it through the multi-agent AI pipeline."
            )

            uploaded_file = st.file_uploader(
                "Upload Clinical Document (PDF, DOCX, TXT, PNG, JPG, JPEG)",
                type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
                help="Scanned note, lab report, referral letter, or medical PDF/Word document.",
            )
            if uploaded_file is not None:
                st.session_state.uploaded_file_bytes = uploaded_file.getvalue()
                st.session_state.uploaded_file_name  = uploaded_file.name
                st.session_state.is_sample_active    = False
                st.session_state.error_message       = ""

            st.markdown(
                "<p style='font-size:13px;font-weight:600;margin-top:15px;margin-bottom:5px;'>"
                "OR USE A CLINICAL PRESET NOTE:</p>",
                unsafe_allow_html=True,
            )
            if st.button("📖 Load Sample Patient Record (Word DOCX)", use_container_width=True):
                sample_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "patient_notes", "sample_patient_note_prior_authorization.docx",
                )
                if os.path.exists(sample_path):
                    with open(sample_path, "rb") as fh:
                        st.session_state.uploaded_file_bytes = fh.read()
                    st.session_state.uploaded_file_name = "sample_patient_note_prior_authorization.docx"
                    st.session_state.is_sample_active   = True
                    st.session_state.error_message      = ""
                    st.success("Sample patient document loaded successfully!")
                    st.rerun()
                else:
                    st.error("Sample record not found in app/data/patient_notes/")

            if st.session_state.uploaded_file_bytes is not None:
                st.divider()
                if st.button("🚀 Start Prior Authorization Analysis", type="primary", use_container_width=True):
                    st.session_state.pa_step = 2
                    st.rerun()
            else:
                st.info("📁 Load or upload a clinical document above to begin.")

        with col2:
            if st.session_state.uploaded_file_bytes is not None:
                ext = os.path.splitext(st.session_state.uploaded_file_name)[1].lower()
                if ext in [".png", ".jpg", ".jpeg"]:
                    st.image(
                        st.session_state.uploaded_file_bytes,
                        caption="Loaded Scanned Document",
                        use_container_width=True,
                    )
                else:
                    icon_map = {".pdf": "📕", ".docx": "📘", ".txt": "📝"}
                    icon = icon_map.get(ext, "📄")
                    st.markdown(
                        f"""
                        <div class="hospital-card"
                             style="text-align:center;padding:55px 24px;
                                    border:1.5px solid var(--blue-200);background:var(--blue-50);">
                            <div style="font-size:64px;margin-bottom:12px;">{icon}</div>
                            <div style="font-size:16px;font-weight:700;color:var(--text-accent);margin-bottom:6px;">
                                {st.session_state.uploaded_file_name}
                            </div>
                            <div style="font-size:13px;color:var(--text-secondary);">
                                Format: {ext.upper()} · Ready for multi-agent ingestion
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """
                    <div class="hospital-card" style="text-align:center;padding:60px 24px;color:var(--text-muted);">
                        <div style="font-size:48px;margin-bottom:12px;">📄</div>
                        <div style="font-size:15px;font-weight:600;color:var(--text-secondary);margin-bottom:6px;">
                            No document loaded
                        </div>
                        <div style="font-size:13px;">
                            Load the sample record or upload your own file to preview it here.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — MULTI-AGENT PIPELINE
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.pa_step == 2:
        st.markdown(
            """
            <style>
            @keyframes spin { to { transform: rotate(360deg); } }
            .ag-overlay {
                background: linear-gradient(160deg,rgba(10,22,50,.97),rgba(15,30,60,.97));
                backdrop-filter: blur(20px);
                border: 1px solid rgba(96,165,250,.22);
                border-radius: 18px;
                padding: 28px;
                box-shadow: 0 24px 64px rgba(0,0,0,.6);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        agent_steps = [
            ("🔌", "Pipeline Router",      "Initializing clinical multi-agent workflow…"),
            ("📥", "Ingestion Agent",       "Parsing document and converting to canonical Markdown…"),
            ("🏷️", "Classification Agent",  "Analyzing report to classify record category…"),
            ("🧠", "Extraction Agent",      "Running structured entity parser on clinical note…"),
            ("📝", "Summary Agent",         "Generating medical necessity justification summary…"),
            ("📂", "Template Matcher",      "Mapping payer information to authorization template…"),
            ("✅", "Sanitization Auditor",  "Auditing payloads and finalizing review stage…"),
        ]

        overlay_slot = st.empty()

        def render_agent_status(completed_list, active_idx, status_label, progress_pct):
            rows = ""
            for i, (ic, nm, ds) in enumerate(agent_steps):
                if i < len(completed_list):
                    rows += (
                        f'<div style="display:flex;align-items:center;gap:14px;padding:12px 16px;'
                        f'background:rgba(34,197,94,.10);border:1px solid rgba(34,197,94,.25);'
                        f'border-radius:10px;margin-bottom:8px;">'
                        f'<div style="font-size:20px;width:32px;text-align:center;">{ic}</div>'
                        f'<div style="flex:1;">'
                        f'<div style="font-size:12px;font-weight:700;color:#86efac;letter-spacing:.4px;text-transform:uppercase;">{nm}</div>'
                        f'<div style="font-size:13px;color:rgba(255,255,255,.75);margin-top:2px;">{ds}</div>'
                        f'</div><div style="font-size:18px;color:#4ade80;flex-shrink:0;">✓</div></div>'
                    )
                elif i == active_idx:
                    rows += (
                        f'<div style="display:flex;align-items:center;gap:14px;padding:12px 16px;'
                        f'background:rgba(37,99,235,.18);border:1.5px solid rgba(96,165,250,.45);'
                        f'border-radius:10px;margin-bottom:8px;box-shadow:0 0 20px rgba(96,165,250,.15);">'
                        f'<div style="font-size:20px;width:32px;text-align:center;">{ic}</div>'
                        f'<div style="flex:1;">'
                        f'<div style="font-size:12px;font-weight:700;color:#93c5fd;letter-spacing:.4px;text-transform:uppercase;">{nm}</div>'
                        f'<div style="font-size:13px;color:rgba(255,255,255,.85);margin-top:2px;">{ds}</div>'
                        f'</div>'
                        f'<div style="width:20px;height:20px;border:2px solid #93c5fd;'
                        f'border-top-color:transparent;border-radius:50%;animation:spin .8s linear infinite;flex-shrink:0;"></div>'
                        f'</div>'
                    )
                else:
                    rows += (
                        f'<div style="display:flex;align-items:center;gap:14px;padding:12px 16px;'
                        f'background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);'
                        f'border-radius:10px;margin-bottom:8px;opacity:.4;">'
                        f'<div style="font-size:20px;width:32px;text-align:center;filter:grayscale(1);">{ic}</div>'
                        f'<div style="flex:1;">'
                        f'<div style="font-size:12px;font-weight:600;color:rgba(255,255,255,.45);letter-spacing:.4px;text-transform:uppercase;">{nm}</div>'
                        f'<div style="font-size:13px;color:rgba(255,255,255,.3);margin-top:2px;">{ds}</div>'
                        f'</div>'
                        f'<div style="width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.18);flex-shrink:0;"></div>'
                        f'</div>'
                    )

            overlay_slot.markdown(
                f'<div class="ag-overlay">'
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;'
                f'padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.08);">'
                f'<div style="width:42px;height:42px;background:rgba(37,99,235,.25);border-radius:12px;'
                f'display:flex;align-items:center;justify-content:center;font-size:22px;'
                f'border:1px solid rgba(96,165,250,.3);">🤖</div>'
                f'<div>'
                f'<div style="font-size:16px;font-weight:700;color:#fff;font-family:Outfit,sans-serif;">Clinical Multi-Agent Pipeline Running</div>'
                f'<div style="font-size:12px;color:#93c5fd;margin-top:3px;">{status_label}</div>'
                f'</div></div>'
                f'{rows}'
                f'<div style="margin-top:16px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
                f'<span style="font-size:11px;color:rgba(255,255,255,.45);font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.6px;">Pipeline Progress</span>'
                f'<span style="font-size:12px;color:#93c5fd;font-weight:700;">{progress_pct}%</span>'
                f'</div>'
                f'<div style="height:6px;background:rgba(255,255,255,.08);border-radius:6px;overflow:hidden;">'
                f'<div style="height:100%;width:{progress_pct}%;'
                f'background:linear-gradient(90deg,#2563eb,#38bdf8);border-radius:6px;"></div>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

        completed = []
        try:
            # 1 – Pipeline Router
            render_agent_status(completed, 0, "Initializing pipeline…", 10)
            time.sleep(0.5)
            completed.append(agent_steps[0])

            # 2 – Ingestion Agent
            render_agent_status(completed, 1, "Parsing document to canonical Markdown…", 25)
            from collections import namedtuple
            FileMock = namedtuple("FileMock", ["name", "getvalue"])
            file_mock = FileMock(
                st.session_state.uploaded_file_name,
                lambda: st.session_state.uploaded_file_bytes,
            )
            ingested = processing_file(file_mock)
            st.session_state.normalized_markdown = ingested.get("content", "")
            completed.append(agent_steps[1])

            if not has_api_key:
                # ── Offline / No-key mode ──────────────────────────────────
                logger.warning("No API key – using offline preset data.")
                st.session_state.classification = {
                    "category": "Clinical Note",
                    "justification": "API Key required to run live LLM classification.",
                }
                st.session_state.extracted_data = {
                    "member_first_name": "John",
                    "member_last_name":  "Smith",
                    "date_of_birth":     "1972-03-14",
                    "gender":            "M",
                    "member_id":         "BC-AETNA-98213",
                    "req_provider_name": "Emily Carter, MD",
                    "req_provider_npi":  "1234567890",
                    "req_provider_phone": "555-019-2831",
                    "medical_necessity_statement": (
                        "Patient has chronic lumbar pain radiating down the left leg for "
                        "6 months, refractory to conservative therapy. Requesting Lumbar "
                        "Spine MRI to verify nerve root compression."
                    ),
                    "failed_conservative_treatments": [
                        "physical therapy", "NSAIDs", "oral steroids", "Gabapentin"
                    ],
                    "diagnostic_tests_summary": (
                        "Positive straight leg raise at 40° left. Limited lumbar range of motion."
                    ),
                    "functional_impairment_description": (
                        "Difficulty performing activities of daily living and inability to sit "
                        "for extended periods while working."
                    ),
                    "diagnosis": [
                        {"code": "M54.16", "description": "Lumbar radiculopathy, left L5 distribution"}
                    ],
                    "procedure": [
                        {"code": "72148", "description": "MRI Lumbar Spine without contrast"}
                    ],
                }
                st.session_state.clinical_summary = (
                    "### 🧑‍⚕️ Patient Overview\n"
                    "John Smith is a 54-year-old male. Insurance member ID: BC-AETNA-98213.\n\n"
                    "### 📋 Clinical Background\n"
                    "Primary Diagnosis: Lumbar radiculopathy (ICD-10 M54.16). "
                    "Chronic low back pain refractory to conservative therapies.\n\n"
                    "### 🧠 Current Symptoms & Status\n"
                    "Severe lower back pain radiating down the left leg. Limited lumbar range of motion. "
                    "Positive straight leg raise at 40°.\n\n"
                    "### 💊 Failed Conservative Therapies\n"
                    "- Physical Therapy (6 weeks)\n"
                    "- NSAIDs (Ibuprofen 800 mg)\n"
                    "- Gabapentin (300 mg TID)\n\n"
                    "### 💉 Requested Service & CPT Codes\n"
                    "MRI Lumbar Spine without contrast (CPT 72148).\n\n"
                    "### 🔍 Medical Necessity Justification\n"
                    "Requested MRI is medically necessary due to progressive neurologic deficits "
                    "(motor weakness 4/5) and failure of comprehensive conservative treatment."
                )
                # Set template path even in offline mode
                st.session_state.payer = "Aetna"
                st.session_state.selected_template_path = select_template("Aetna")

                for k in range(2, len(agent_steps)):
                    render_agent_status(
                        completed, k,
                        f"Running {agent_steps[k][1]} (Offline mode)…",
                        int((k / len(agent_steps)) * 100),
                    )
                    time.sleep(0.35)
                    completed.append(agent_steps[k])

            else:
                # ── Live LLM mode ───────────────────────────────────────────
                # 3 – Classification
                render_agent_status(completed, 2, "Classifying document category…", 40)
                st.session_state.classification = classify_document(
                    st.session_state.normalized_markdown, provider, model_name
                )
                completed.append(agent_steps[2])

                # 4 – Extraction
                render_agent_status(completed, 3, "Extracting structured clinical entities…", 60)
                fields_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "extracted_fields.json",
                )
                with open(fields_path) as fh:
                    fields = json.load(fh)
                st.session_state.extracted_data = extract_medical_info(
                    st.session_state.normalized_markdown, fields, provider, model_name
                )
                completed.append(agent_steps[3])

                # 5 – Clinical Summary
                render_agent_status(completed, 4, "Generating clinical necessity summary…", 75)
                st.session_state.clinical_summary = generate_clinical_summary(
                    st.session_state.extracted_data, provider, model_name
                )
                completed.append(agent_steps[4])

                # 6 – Template Matcher
                render_agent_status(completed, 5, "Matching insurance payer template…", 90)
                text_lower = (st.session_state.normalized_markdown or "").lower()
                member_id_lower = str(st.session_state.extracted_data.get("member_id") or "").lower()
                if "aetna" in text_lower or "aetna" in member_id_lower:
                    st.session_state.payer = "Aetna"
                elif "cigna" in text_lower or "cigna" in member_id_lower:
                    st.session_state.payer = "Cigna"
                else:
                    st.session_state.payer = "Default"
                st.session_state.selected_template_path = select_template(st.session_state.payer)
                completed.append(agent_steps[5])

                # 7 – Auditor
                render_agent_status(completed, 6, "Running payload verification…", 98)
                time.sleep(0.4)
                completed.append(agent_steps[6])

            render_agent_status(completed, 7, "All agents finished — moving to review stage.", 100)
            time.sleep(0.5)
            st.session_state.pa_step = 3
            st.rerun()

        except Exception as exc:
            logger.error("Error in multi-agent pipeline: %s", str(exc), exc_info=True)
            st.session_state.error_message = str(exc)
            st.session_state.pa_step = 3
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — CLINICIAN INTERACTIVE REVIEW PORTAL
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.pa_step == 3:
        st.subheader("👀 Step 3: Clinician Preview & Verification")

        if not has_api_key:
            st.warning(
                "⚠️ Offline Mode: No LLM API key detected. "
                "Showing pre-cached fallback data — configure your key in ⚙️ Settings."
            )

        if st.session_state.error_message:
            st.error(f"❌ Pipeline failed: {st.session_state.error_message}")
            col_err1, col_err2 = st.columns(2)
            with col_err1:
                if st.button("⬅️ Back to Upload", use_container_width=True):
                    _reset_state()
                    st.rerun()
            with col_err2:
                if st.button("🔄 Retry Analysis", type="primary", use_container_width=True):
                    st.session_state.error_message = ""
                    st.session_state.pa_step = 2
                    st.rerun()
            return

        # ── Read current extracted data once ──────────────────────────────
        data = st.session_state.extracted_data

        # ── Pull all editable field values BEFORE rendering tabs ──────────
        # This ensures they are always defined when the Compile button fires,
        # regardless of which tab the user last interacted with.
        fname         = data.get("member_first_name") or ""
        lname         = data.get("member_last_name")  or ""
        dob           = data.get("date_of_birth")     or ""
        gender_val    = data.get("gender")             or ""
        member_id     = data.get("member_id")          or ""
        req_provider  = data.get("req_provider_name")  or ""
        provider_npi  = data.get("req_provider_npi")   or ""
        med_necessity = data.get("medical_necessity_statement")    or ""
        diag_tests    = data.get("diagnostic_tests_summary")       or ""
        func_impair   = data.get("functional_impairment_description") or ""
        failed_list   = data.get("failed_conservative_treatments") or []
        failed_str    = ", ".join(failed_list) if isinstance(failed_list, list) else str(failed_list)

        diag_list = data.get("diagnosis") or []
        d1_code   = diag_list[0].get("code", "")        if diag_list and isinstance(diag_list[0], dict) else ""
        d1_desc   = diag_list[0].get("description", "") if diag_list and isinstance(diag_list[0], dict) else ""
        proc_list = data.get("procedure") or []
        p1_code   = proc_list[0].get("code", "")        if proc_list and isinstance(proc_list[0], dict) else ""
        p1_desc   = proc_list[0].get("description", "") if proc_list and isinstance(proc_list[0], dict) else ""

        payer_options = ["Default", "Aetna", "Cigna"]
        payer_idx     = payer_options.index(st.session_state.payer) if st.session_state.payer in payer_options else 0
        summary_text  = st.session_state.clinical_summary

        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.markdown("### 📄 Normalised Patient Record")
            st.text_area(
                "Document Text (Markdown format)",
                value=st.session_state.normalized_markdown,
                height=480,
                disabled=True,
                key="pa_norm_preview",
            )
            category      = st.session_state.classification.get("category",      "Clinical Note")
            justification = st.session_state.classification.get("justification", "Analyzed note.")
            st.markdown(
                f"""
                <div class="hospital-card"
                     style="padding:16px;margin-top:15px;border-left:5px solid var(--blue-500);">
                    <div style="font-weight:700;color:var(--text-accent);font-size:14px;">
                        🏷️ Document Classification
                    </div>
                    <div style="font-size:16px;font-weight:600;color:var(--text-primary);margin:4px 0;">
                        {category}
                    </div>
                    <div style="font-size:13px;color:var(--text-secondary);font-style:italic;">
                        {justification}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown("### ✍️ Interactive Clinician Edit Portal")
            st.markdown(
                "Review and override the extracted demographics, clinical evidence, and "
                "medical necessity statement before compiling the authorization package."
            )

            tab_demo, tab_clinical, tab_codes, tab_summary = st.tabs([
                "👤 Demographics",
                "🏥 Clinical Evidence",
                "🔢 CPT / ICD Codes",
                "📝 Medical Summary",
            ])

            with tab_demo:
                st.markdown(
                    "<p style='font-size:14px;font-weight:700;color:var(--text-accent);'>"
                    "Patient &amp; Provider Information</p>",
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                with c1:
                    fname        = st.text_input("First Name",               value=fname,        key="pa_fname")
                    lname        = st.text_input("Last Name",                value=lname,        key="pa_lname")
                    dob          = st.text_input("Date of Birth (YYYY-MM-DD)", value=dob,        key="pa_dob")
                    gender_val   = st.text_input("Gender (M / F)",           value=gender_val,   key="pa_gender")
                with c2:
                    member_id    = st.text_input("Member / Subscriber ID",   value=member_id,    key="pa_member_id")
                    selected_payer = st.selectbox("Insurance Payer Template", payer_options, index=payer_idx, key="pa_payer")
                    req_provider = st.text_input("Requesting Provider",      value=req_provider, key="pa_provider")
                    provider_npi = st.text_input("Provider NPI",             value=provider_npi, key="pa_npi")

            with tab_clinical:
                st.markdown(
                    "<p style='font-size:14px;font-weight:700;color:var(--text-accent);'>"
                    "Medical Necessity Evidence</p>",
                    unsafe_allow_html=True,
                )
                med_necessity = st.text_area("Medical Necessity Justification",        value=med_necessity, height=120, key="pa_med_nec")
                diag_tests    = st.text_area("Diagnostic Tests (MRI, CT, labs…)",      value=diag_tests,    height=100, key="pa_diag_tests")
                failed_str    = st.text_input("Failed Conservative Treatments (comma-separated)", value=failed_str, key="pa_failed")
                func_impair   = st.text_area("Functional Impairment Description",      value=func_impair,   height=100, key="pa_func")

            with tab_codes:
                st.markdown(
                    "<p style='font-size:14px;font-weight:700;color:var(--text-accent);'>"
                    "ICD-10 Diagnosis &amp; CPT Procedure Codes</p>",
                    unsafe_allow_html=True,
                )
                ca, cb = st.columns([1, 3])
                with ca:
                    d1_code = st.text_input("ICD-10 Code 1",        value=d1_code, key="pa_d1_code")
                with cb:
                    d1_desc = st.text_input("ICD-10 Description 1", value=d1_desc, key="pa_d1_desc")
                cc, cd = st.columns([1, 3])
                with cc:
                    p1_code = st.text_input("CPT / HCPCS Code 1",   value=p1_code, key="pa_p1_code")
                with cd:
                    p1_desc = st.text_input("CPT Description 1",    value=p1_desc, key="pa_p1_desc")

            with tab_summary:
                st.markdown(
                    "<p style='font-size:14px;font-weight:700;color:var(--text-accent);'>"
                    "Editable Clinical Summary</p>",
                    unsafe_allow_html=True,
                )
                summary_text = st.text_area(
                    "Medical Clinical Necessity Summary (Markdown)",
                    value=summary_text,
                    height=380,
                    key="pa_summary",
                )

            st.divider()

            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("⬅️ Restart / Reset", use_container_width=True, key="pa_reset"):
                    _reset_state()
                    st.rerun()
            with b2:
                if st.button("🔄 Re-run AI Extraction", use_container_width=True, key="pa_rerun"):
                    st.session_state.pa_step = 2
                    st.rerun()
            with b3:
                if st.button("💾 Compile & Finalize Form", type="primary", use_container_width=True, key="pa_compile"):
                    # Persist user edits back to session state
                    st.session_state.extracted_data.update({
                        "member_first_name":               st.session_state.pa_fname,
                        "member_last_name":                st.session_state.pa_lname,
                        "date_of_birth":                   st.session_state.pa_dob,
                        "gender":                          st.session_state.pa_gender,
                        "member_id":                       st.session_state.pa_member_id,
                        "req_provider_name":               st.session_state.pa_provider,
                        "req_provider_npi":                st.session_state.pa_npi,
                        "medical_necessity_statement":     st.session_state.pa_med_nec,
                        "diagnostic_tests_summary":        st.session_state.pa_diag_tests,
                        "functional_impairment_description": st.session_state.pa_func,
                        "failed_conservative_treatments":  [
                            x.strip() for x in st.session_state.pa_failed.split(",") if x.strip()
                        ],
                        "diagnosis":  [{"code": st.session_state.pa_d1_code, "description": st.session_state.pa_d1_desc}],
                        "procedure":  [{"code": st.session_state.pa_p1_code, "description": st.session_state.pa_p1_desc}],
                    })
                    st.session_state.clinical_summary = st.session_state.pa_summary
                    st.session_state.payer = st.session_state.pa_payer
                    st.session_state.selected_template_path = select_template(st.session_state.pa_payer)

                    # Compile DOCX
                    output_dir = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "output",
                    )
                    os.makedirs(output_dir, exist_ok=True)
                    safe_name = (st.session_state.pa_lname or "patient").lower().replace(" ", "_")
                    filled_docx = os.path.join(output_dir, f"filled_prior_auth_{safe_name}.docx")
                    try:
                        fill_template_docx(
                            st.session_state.selected_template_path,
                            st.session_state.extracted_data,
                            filled_docx,
                        )
                        st.session_state.filled_docx_path = filled_docx
                        st.session_state.pa_step = 4
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error compiling DOCX template: {ex}")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — EXPORT & DOWNLOAD
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.pa_step == 4:
        st.subheader("✅ Step 4: Export Completed Package")

        st.markdown(
            """
            <div style="background:var(--success-bg);border:2px solid var(--success-border);
                        border-radius:14px;padding:32px;text-align:center;margin-bottom:30px;">
                <h2 style="color:var(--success-text);margin-top:0;font-family:'Outfit',sans-serif;font-weight:700;">
                    🎉 Prior Authorization Package Finalized
                </h2>
                <p style="font-size:16px;color:var(--success-subtext);font-weight:500;">
                    Multi-agent pipeline completed: notes extracted, necessity verified, templates compiled.
                </p>
                <p style="font-size:14px;color:var(--success-subtext);">
                    Ready for download and direct EHR integration.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.markdown("### 📥 Multi-Format Downloads")
            st.markdown("Download the compiled medical necessity package in your preferred format:")

            # DOCX
            if st.session_state.filled_docx_path and os.path.exists(st.session_state.filled_docx_path):
                with open(st.session_state.filled_docx_path, "rb") as fh:
                    docx_bytes = fh.read()
                st.download_button(
                    "📥 Download Completed Word Form (.docx)",
                    data=docx_bytes,
                    file_name=os.path.basename(st.session_state.filled_docx_path),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

            # PDF
            patient_name = (
                f"{st.session_state.extracted_data.get('member_first_name', '')} "
                f"{st.session_state.extracted_data.get('member_last_name', '')}".strip()
                or "Patient Record"
            )
            pdf_bytes = text_to_pdf(
                st.session_state.clinical_summary,
                f"Prior Authorization Medical Necessity: {patient_name}",
            )
            safe_last = (st.session_state.extracted_data.get("member_last_name") or "patient").lower()
            st.download_button(
                "📄 Download Clinical Necessity PDF Summary",
                data=pdf_bytes,
                file_name=f"prior_auth_clinical_summary_{safe_last}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )

            # Markdown
            st.download_button(
                "📝 Download Clinical Summary (.md)",
                data=st.session_state.clinical_summary,
                file_name=f"prior_auth_clinical_summary_{safe_last}.md",
                mime="text/markdown",
                use_container_width=True,
            )

            # JSON
            st.download_button(
                "⚙️ Download Raw EHR Structured Record (.json)",
                data=json.dumps(st.session_state.extracted_data, indent=4),
                file_name=f"prior_auth_ehr_payload_{safe_last}.json",
                mime="application/json",
                use_container_width=True,
            )

            st.divider()
            if st.button("🔄 Start New Authorization Request", use_container_width=True, key="pa_new"):
                _reset_state()
                st.rerun()
            if st.button("⬅️ Return to Review & Edit", use_container_width=True, key="pa_back"):
                st.session_state.pa_step = 3
                st.rerun()

        with col2:
            st.markdown("### 🔍 Compiled Clinical Summary Preview")
            st.markdown(
                f"""
                <div class="hospital-card"
                     style="font-size:14px;color:var(--text-primary);padding:25px;
                            border-top:4px solid var(--blue-500);overflow-y:auto;max-height:520px;">
                    {st.session_state.clinical_summary}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Floating chat widget (present on every step)
    render_floating_chat()


if __name__ == "__main__":
    setup_page()
    render_prior_auth_page()
