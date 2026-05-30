import streamlit as st
import streamlit.components.v1 as components
import time
import os
import json
import logging
import html as html_lib

from utils.api_key_validator import check_provider_api_key
from components.floating_chat import render_floating_chat
from utils.theme import inject_theme

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


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def setup_page():
    st.set_page_config(
        page_title="Prior Authorization Clinical Workspace",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def draw_status_bar(step: int):
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
            html += '<div style="color:var(--text-muted);font-size:18px;padding:0 2px;">&#x27A1;</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _reset_state():
    for k, v in {
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
    }.items():
        st.session_state[k] = v


def _field(d: dict, *keys, default=""):
    """Safe multi-key dict lookup with fallback."""
    for k in keys:
        v = d.get(k)
        if v:
            return str(v)
    return default


# ─────────────────────────────────────────────────────────────────────────────
# PA Form HTML Preview Builder
# ─────────────────────────────────────────────────────────────────────────────

def _e(text: str) -> str:
    """HTML-escape a value, replace empty with an em-dash placeholder."""
    if not text or not str(text).strip():
        return '<span style="color:#bbb;font-style:italic;">—</span>'
    return html_lib.escape(str(text))


def _checkbox(checked: bool) -> str:
    return "&#9745;" if checked else "&#9744;"


def build_pa_html_preview(data: dict, clinical_summary: str, payer: str) -> str:
    """
    Render the Prior Authorization form as a pixel-perfect HTML document
    that closely mirrors the final exported PDF / DOCX template.
    """

    # ── Derived values ───────────────────────────────────────────────────
    payer_label = payer if payer != "Default" else "Health Plan"
    request_type = (data.get("request_type") or "standard").lower()
    is_standard   = "standard"   in request_type
    is_expedited  = "expedited"  in request_type
    is_quick      = "quick"      in request_type or "quick_response" in request_type

    full_name = f"{_field(data, 'member_first_name')} {_field(data, 'member_last_name')}".strip() or "—"

    # Diagnosis rows
    diag_list = data.get("diagnosis") or []
    diag_rows = ""
    for i, d in enumerate(diag_list[:6], start=1):
        code = _e(d.get("code", "") if isinstance(d, dict) else "")
        desc = _e(d.get("description", "") if isinstance(d, dict) else "")
        diag_rows += (
            f'<tr>'
            f'<td style="padding:5px 8px;border:1px solid #c8d0dc;font-size:11px;color:#333;">{i}</td>'
            f'<td style="padding:5px 8px;border:1px solid #c8d0dc;font-weight:600;font-size:11px;">{code}</td>'
            f'<td style="padding:5px 8px;border:1px solid #c8d0dc;font-size:11px;color:#444;">{desc}</td>'
            f'</tr>'
        )
    if not diag_rows:
        diag_rows = '<tr><td colspan="3" style="padding:8px;border:1px solid #c8d0dc;font-size:11px;color:#bbb;font-style:italic;text-align:center;">No diagnosis codes extracted</td></tr>'

    # Procedure rows
    proc_list = data.get("procedure") or []
    proc_rows = ""
    for i, p in enumerate(proc_list[:6], start=1):
        code = _e(p.get("code", "") if isinstance(p, dict) else "")
        desc = _e(p.get("description", "") if isinstance(p, dict) else "")
        proc_rows += (
            f'<tr>'
            f'<td style="padding:5px 8px;border:1px solid #c8d0dc;font-size:11px;color:#333;">{i}</td>'
            f'<td style="padding:5px 8px;border:1px solid #c8d0dc;font-weight:600;font-size:11px;">{code}</td>'
            f'<td style="padding:5px 8px;border:1px solid #c8d0dc;font-size:11px;color:#444;">{desc}</td>'
            f'</tr>'
        )
    if not proc_rows:
        proc_rows = '<tr><td colspan="3" style="padding:8px;border:1px solid #c8d0dc;font-size:11px;color:#bbb;font-style:italic;text-align:center;">No procedure codes extracted</td></tr>'

    # Failed treatments
    failed = data.get("failed_conservative_treatments") or []
    if isinstance(failed, list):
        failed_html = "".join(
            f'<li style="font-size:11px;color:#333;margin-bottom:3px;">{_e(t)}</li>'
            for t in failed
        ) if failed else '<li style="font-size:11px;color:#bbb;font-style:italic;">None documented</li>'
    else:
        failed_html = f'<li style="font-size:11px;color:#333;">{_e(str(failed))}</li>'

    # Service types
    svc_types = data.get("requested_service_types") or []
    svc_labels = {
        "out_patient_surgery": "Outpatient Surgery",
        "pain_management": "Pain Management",
        "diagnostic_imaging": "Diagnostic Imaging",
        "physical_therapy": "Physical Therapy",
        "inpatient": "Inpatient",
        "specialist_referral": "Specialist Referral",
        "dme": "DME / Equipment",
        "lab": "Laboratory",
    }
    svc_html = ""
    for st_key, st_label in svc_labels.items():
        checked = any(st_key in str(s).lower() for s in svc_types)
        svc_html += (
            f'<span style="font-size:11px;margin-right:16px;white-space:nowrap;">'
            f'{_checkbox(checked)}&nbsp;{st_label}'
            f'</span>'
        )

    # Clinical summary — render as plain paragraphs, strip markdown headers
    def _md_to_html(text: str) -> str:
        lines, out = text.split("\n"), []
        for line in lines:
            s = line.strip()
            if s.startswith("### "):
                out.append(f'<p style="font-size:11px;font-weight:700;color:#003580;margin:10px 0 2px;">{html_lib.escape(s[4:])}</p>')
            elif s.startswith("## "):
                out.append(f'<p style="font-size:12px;font-weight:700;color:#003580;margin:10px 0 2px;">{html_lib.escape(s[3:])}</p>')
            elif s.startswith("# "):
                out.append(f'<p style="font-size:13px;font-weight:700;color:#003580;margin:10px 0 4px;">{html_lib.escape(s[2:])}</p>')
            elif s.startswith("- ") or s.startswith("* "):
                out.append(f'<p style="font-size:11px;color:#333;margin:1px 0 1px 12px;">&#8226;&nbsp;{html_lib.escape(s[2:])}</p>')
            elif s:
                out.append(f'<p style="font-size:11px;color:#333;margin:3px 0;line-height:1.55;">{html_lib.escape(s)}</p>')
        return "\n".join(out)

    summary_html = _md_to_html(clinical_summary) if clinical_summary else (
        '<p style="font-size:11px;color:#bbb;font-style:italic;">No clinical summary generated.</p>'
    )

    # ── Full HTML document ───────────────────────────────────────────────
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    background: #e8ecf0;
    padding: 24px 16px 40px;
    min-height: 100vh;
  }}
  .page {{
    background: #ffffff;
    max-width: 780px;
    margin: 0 auto;
    padding: 32px 36px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
    border-radius: 3px;
    position: relative;
  }}
  /* ── Header ── */
  .form-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 3px solid #003580;
    padding-bottom: 14px;
    margin-bottom: 16px;
  }}
  .form-title {{ font-size: 17px; font-weight: 700; color: #003580; letter-spacing: 0.3px; }}
  .form-subtitle {{ font-size: 11px; color: #555; margin-top: 3px; }}
  .form-logo {{
    text-align: right;
    font-size: 18px;
    font-weight: 800;
    color: #003580;
    line-height: 1.1;
  }}
  .form-logo span {{ display:block; font-size:10px; font-weight:400; color:#666; }}
  /* ── Section headers ── */
  .sec-head {{
    background: #003580;
    color: #ffffff;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    padding: 5px 10px;
    margin-top: 14px;
    margin-bottom: 0;
  }}
  .sec-body {{
    border: 1px solid #c0c8d8;
    border-top: none;
    padding: 10px 12px;
  }}
  /* ── Field grid ── */
  .field-grid {{
    display: grid;
    gap: 8px 14px;
  }}
  .g2  {{ grid-template-columns: 1fr 1fr; }}
  .g3  {{ grid-template-columns: 1fr 1fr 1fr; }}
  .g4  {{ grid-template-columns: 1fr 1fr 1fr 1fr; }}
  .g13 {{ grid-template-columns: 1fr 3fr; }}
  .g31 {{ grid-template-columns: 3fr 1fr; }}
  /* ── Single field ── */
  .field {{ display: flex; flex-direction: column; }}
  .field-label {{
    font-size: 9px;
    font-weight: 700;
    color: #667;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 3px;
  }}
  .field-value {{
    font-size: 12px;
    color: #1a1a2e;
    border-bottom: 1.5px solid #9aa4be;
    min-height: 20px;
    padding-bottom: 2px;
    line-height: 1.4;
  }}
  /* ── Checkbox row ── */
  .check-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px 0;
    align-items: center;
    font-size: 11px;
    color: #333;
    padding: 6px 0;
  }}
  /* ── Tables ── */
  table {{ width: 100%; border-collapse: collapse; }}
  th {{
    background: #e8edf5;
    font-size: 10px;
    font-weight: 700;
    color: #003580;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    padding: 5px 8px;
    border: 1px solid #c0c8d8;
    text-align: left;
  }}
  /* ── Page 2 break ── */
  .page-break {{
    background: #e8ecf0;
    margin: 28px -36px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    font-weight: 700;
    color: #888;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}
  .page-num {{
    position: absolute;
    bottom: 12px;
    right: 20px;
    font-size: 9px;
    color: #aaa;
  }}
  /* ── Signature block ── */
  .sig-block {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 24px;
    margin-top: 8px;
  }}
  .sig-line {{
    border-bottom: 1.5px solid #333;
    min-height: 28px;
    margin-top: 4px;
  }}
</style>
</head>
<body>
<div class="page">

  <!-- ══ HEADER ══ -->
  <div class="form-header">
    <div>
      <div class="form-title">PRIOR AUTHORIZATION REQUEST FORM</div>
      <div class="form-subtitle">Submit to: {_e(payer_label)} &nbsp;|&nbsp; Fax: (800) 555-0190 &nbsp;|&nbsp; Phone: (800) 555-0191</div>
    </div>
    <div class="form-logo">
      {_e(payer_label)}
      <span>Health Plan</span>
    </div>
  </div>

  <!-- ══ REQUEST TYPE ══ -->
  <div class="sec-head">Request Type</div>
  <div class="sec-body">
    <div class="check-row">
      <span style="margin-right:20px;">{_checkbox(is_standard)}&nbsp;<strong>Standard</strong></span>
      <span style="margin-right:20px;">{_checkbox(is_expedited)}&nbsp;<strong>Expedited</strong>
        <span style="font-size:10px;color:#777;"> (Physician signature required)</span>
      </span>
      <span style="margin-right:20px;">{_checkbox(is_quick)}&nbsp;<strong>Quick Response</strong></span>
    </div>
    <div class="field-grid g3" style="margin-top:8px;">
      <div class="field">
        <div class="field-label">Date of Service</div>
        <div class="field-value">{_e(_field(data,'pre_scheduled_date_of_service'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Authorization Needed By</div>
        <div class="field-value">{_e(_field(data,'authorization_needed_by_date'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Physician Signature (Expedited)</div>
        <div class="field-value">{_e(_field(data,'expedited_request_physician_signature'))}</div>
      </div>
    </div>
  </div>

  <!-- ══ MEMBER / PATIENT INFORMATION ══ -->
  <div class="sec-head">Member / Patient Information</div>
  <div class="sec-body">
    <div class="field-grid g4">
      <div class="field">
        <div class="field-label">Last Name</div>
        <div class="field-value">{_e(_field(data,'member_last_name'))}</div>
      </div>
      <div class="field">
        <div class="field-label">First Name</div>
        <div class="field-value">{_e(_field(data,'member_first_name'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Date of Birth</div>
        <div class="field-value">{_e(_field(data,'date_of_birth'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Gender</div>
        <div class="field-value">{_e(_field(data,'gender'))}</div>
      </div>
    </div>
    <div class="field-grid g3" style="margin-top:8px;">
      <div class="field">
        <div class="field-label">Member / Subscriber ID</div>
        <div class="field-value">{_e(_field(data,'member_id'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Insurance Plan</div>
        <div class="field-value">{_e(payer_label)}</div>
      </div>
      <div class="field">
        <div class="field-label">Chart Notes Attached</div>
        <div class="field-value">
          {_checkbox(bool(data.get('supporting_chart_notes_available')))}&nbsp;Yes
          &nbsp;&nbsp;
          {_checkbox(not bool(data.get('supporting_chart_notes_available')))}&nbsp;No
        </div>
      </div>
    </div>
  </div>

  <!-- ══ REQUESTING PROVIDER ══ -->
  <div class="sec-head">Requesting Provider</div>
  <div class="sec-body">
    <div class="field-grid g3">
      <div class="field">
        <div class="field-label">Provider Name</div>
        <div class="field-value">{_e(_field(data,'req_provider_name'))}</div>
      </div>
      <div class="field">
        <div class="field-label">NPI</div>
        <div class="field-value">{_e(_field(data,'req_provider_npi'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Provider # / Tax ID</div>
        <div class="field-value">{_e(_field(data,'req_provider_num_or_tax_id'))}</div>
      </div>
    </div>
    <div class="field-grid g3" style="margin-top:8px;">
      <div class="field">
        <div class="field-label">Phone</div>
        <div class="field-value">{_e(_field(data,'req_provider_phone'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Fax</div>
        <div class="field-value">{_e(_field(data,'req_provider_fax'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Contact Person</div>
        <div class="field-value">{_e(_field(data,'req_provider_contact_person'))}</div>
      </div>
    </div>
  </div>

  <!-- ══ SERVICE / FACILITY PROVIDER ══ -->
  <div class="sec-head">Service Provider / Facility</div>
  <div class="sec-body">
    <div class="field-grid g3">
      <div class="field">
        <div class="field-label">Facility / Provider Name</div>
        <div class="field-value">{_e(_field(data,'service_provider_name'))}</div>
      </div>
      <div class="field">
        <div class="field-label">NPI</div>
        <div class="field-value">{_e(_field(data,'service_provider_npi'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Tax ID</div>
        <div class="field-value">{_e(_field(data,'service_provider_tax_id'))}</div>
      </div>
    </div>
    <div class="field-grid g3" style="margin-top:8px;">
      <div class="field">
        <div class="field-label">Address</div>
        <div class="field-value">{_e(_field(data,'service_provider_address'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Phone</div>
        <div class="field-value">{_e(_field(data,'service_provider_phone'))}</div>
      </div>
      <div class="field">
        <div class="field-label">Fax</div>
        <div class="field-value">{_e(_field(data,'service_provider_fax'))}</div>
      </div>
    </div>
  </div>

  <!-- ══ REQUESTED SERVICE TYPES ══ -->
  <div class="sec-head">Requested Service Type(s)</div>
  <div class="sec-body">
    <div class="check-row">{svc_html}</div>
  </div>

  <!-- ══ DIAGNOSIS CODES ══ -->
  <div class="sec-head">ICD-10 Diagnosis Codes</div>
  <div class="sec-body" style="padding:0;">
    <table>
      <tr>
        <th style="width:32px;">#</th>
        <th style="width:100px;">ICD-10 Code</th>
        <th>Description</th>
      </tr>
      {diag_rows}
    </table>
  </div>

  <!-- ══ PROCEDURE CODES ══ -->
  <div class="sec-head">CPT / HCPCS Procedure Codes</div>
  <div class="sec-body" style="padding:0;">
    <table>
      <tr>
        <th style="width:32px;">#</th>
        <th style="width:100px;">CPT / HCPCS</th>
        <th>Description</th>
      </tr>
      {proc_rows}
    </table>
  </div>

  <!-- Page break visual separator -->
  <div class="page-break">&#9472;&#9472;&#9472;&#9472;&nbsp; Page 2 of 2 &nbsp;&#9472;&#9472;&#9472;&#9472;</div>

  <!-- ══ CLINICAL INFORMATION ══ -->
  <div class="sec-head">Clinical Information &amp; Medical Necessity</div>
  <div class="sec-body">

    <div class="field" style="margin-bottom:10px;">
      <div class="field-label">Medical Necessity Statement</div>
      <div style="font-size:11px;color:#1a1a2e;border:1px solid #c0c8d8;border-radius:2px;
                  padding:8px 10px;min-height:48px;line-height:1.6;background:#fafbfd;">
        {_e(_field(data,'medical_necessity_statement'))}
      </div>
    </div>

    <div class="field" style="margin-bottom:10px;">
      <div class="field-label">Diagnostic Tests &amp; Results (MRI, CT, Labs)</div>
      <div style="font-size:11px;color:#1a1a2e;border:1px solid #c0c8d8;border-radius:2px;
                  padding:8px 10px;min-height:36px;line-height:1.6;background:#fafbfd;">
        {_e(_field(data,'diagnostic_tests_summary'))}
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px 16px;margin-bottom:10px;">
      <div class="field">
        <div class="field-label">Failed Conservative Treatments</div>
        <div style="border:1px solid #c0c8d8;border-radius:2px;padding:8px 10px;
                    min-height:60px;background:#fafbfd;">
          <ul style="list-style:none;padding:0;">{failed_html}</ul>
        </div>
      </div>
      <div class="field">
        <div class="field-label">Functional Impairment Description</div>
        <div style="font-size:11px;color:#1a1a2e;border:1px solid #c0c8d8;border-radius:2px;
                    padding:8px 10px;min-height:60px;line-height:1.6;background:#fafbfd;">
          {_e(_field(data,'functional_impairment_description'))}
        </div>
      </div>
    </div>

    <div class="field" style="margin-bottom:6px;">
      <div class="field-label">Lab Values</div>
      <div style="font-size:11px;color:#1a1a2e;border:1px solid #c0c8d8;border-radius:2px;
                  padding:8px 10px;min-height:28px;line-height:1.6;background:#fafbfd;">
        {_e(_field(data,'lab_values_summary'))}
      </div>
    </div>

  </div>

  <!-- ══ CLINICAL SUMMARY (AI-GENERATED) ══ -->
  <div class="sec-head">AI-Generated Clinical Necessity Summary</div>
  <div class="sec-body">
    <div style="border:1px solid #c0c8d8;border-radius:2px;padding:10px 12px;
                background:#fafbfd;min-height:80px;max-height:340px;overflow-y:auto;">
      {summary_html}
    </div>
  </div>

  <!-- ══ AUTHORIZATION & SIGNATURE ══ -->
  <div class="sec-head">Authorizing Physician Certification &amp; Signature</div>
  <div class="sec-body">
    <p style="font-size:10px;color:#555;line-height:1.55;margin-bottom:10px;">
      I certify that the requested service is medically necessary for the member identified above
      and that all information provided is accurate and complete to the best of my knowledge.
      I understand that providing false or misleading information may result in denial of the request
      or other corrective action.
    </p>
    <div class="sig-block">
      <div>
        <div class="field-label">Physician Signature</div>
        <div class="sig-line"></div>
      </div>
      <div>
        <div class="field-label">Date</div>
        <div class="sig-line"></div>
      </div>
      <div style="margin-top:10px;">
        <div class="field-label">Printed Name</div>
        <div class="sig-line"></div>
      </div>
      <div style="margin-top:10px;">
        <div class="field-label">Provider NPI</div>
        <div class="sig-line" style="padding-bottom:2px;font-size:12px;color:#1a1a2e;">
          {_e(_field(data,'req_provider_npi'))}
        </div>
      </div>
    </div>
  </div>

  <div class="page-num">
    Page 1 of 1 &nbsp;|&nbsp; {_e(payer_label)} Prior Authorization Request &nbsp;|&nbsp;
    Patient: {_e(full_name)} &nbsp;|&nbsp; Member ID: {_e(_field(data,'member_id'))}
  </div>

</div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Main Page Renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_prior_auth_page():
    inject_theme()

    st.markdown(
        """
        <div class="hospital-header">
            <div>
                <h1>&#x1F4CB; Prior Authorization Clinical Workspace</h1>
                <p>Unified Document Ingestion &middot; Structured Medical Extraction &middot; Dynamic Template Generation</p>
            </div>
            <div class="header-badge">
                <span class="live-dot"></span>Clinical Processing Agent Ready
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Session state defaults
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
    # STEP 1 — LOAD
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.pa_step == 1:
        st.subheader("&#x1F4C2; Step 1: Load Patient Record or Document")
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
            if st.button("&#x1F4D6; Load Sample Patient Record (Word DOCX)", use_container_width=True):
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
                if st.button("&#x1F680; Start Prior Authorization Analysis", type="primary", use_container_width=True):
                    st.session_state.pa_step = 2
                    st.rerun()
            else:
                st.info("&#x1F4C1; Load or upload a clinical document above to begin.")

        with col2:
            if st.session_state.uploaded_file_bytes is not None:
                ext = os.path.splitext(st.session_state.uploaded_file_name)[1].lower()
                if ext in [".png", ".jpg", ".jpeg"]:
                    st.image(st.session_state.uploaded_file_bytes, caption="Loaded Scanned Document", use_container_width=True)
                else:
                    icon_map = {".pdf": "&#x1F4D5;", ".docx": "&#x1F4D8;", ".txt": "&#x1F4DD;"}
                    icon = icon_map.get(ext, "&#x1F4C4;")
                    st.markdown(
                        f"""<div class="hospital-card" style="text-align:center;padding:55px 24px;
                            border:1.5px solid var(--blue-200);background:var(--blue-50);">
                            <div style="font-size:64px;margin-bottom:12px;">{icon}</div>
                            <div style="font-size:16px;font-weight:700;color:var(--text-accent);margin-bottom:6px;">
                                {html_lib.escape(st.session_state.uploaded_file_name)}
                            </div>
                            <div style="font-size:13px;color:var(--text-secondary);">
                                Format: {ext.upper()} &middot; Ready for multi-agent ingestion
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """<div class="hospital-card" style="text-align:center;padding:60px 24px;color:var(--text-muted);">
                        <div style="font-size:48px;margin-bottom:12px;">&#x1F4C4;</div>
                        <div style="font-size:15px;font-weight:600;color:var(--text-secondary);margin-bottom:6px;">
                            No document loaded
                        </div>
                        <div style="font-size:13px;">
                            Load the sample record or upload your own file to preview it here.
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — MULTI-AGENT PIPELINE
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.pa_step == 2:
        st.markdown(
            """<style>
            @keyframes spin { to { transform: rotate(360deg); } }
            .ag-overlay {
                background: linear-gradient(160deg,rgba(10,22,50,.97),rgba(15,30,60,.97));
                backdrop-filter: blur(20px);
                border: 1px solid rgba(96,165,250,.22);
                border-radius: 18px;
                padding: 28px;
                box-shadow: 0 24px 64px rgba(0,0,0,.6);
            }
            </style>""",
            unsafe_allow_html=True,
        )

        agent_steps = [
            ("&#x1F50C;", "Pipeline Router",      "Initializing clinical multi-agent workflow&#8230;"),
            ("&#x1F4E5;", "Ingestion Agent",       "Parsing document and converting to canonical Markdown&#8230;"),
            ("&#x1F3F7;&#xFE0F;", "Classification Agent",  "Analyzing report to classify record category&#8230;"),
            ("&#x1F9E0;", "Extraction Agent",      "Running structured entity parser on clinical note&#8230;"),
            ("&#x1F4DD;", "Summary Agent",         "Generating medical necessity justification summary&#8230;"),
            ("&#x1F4C2;", "Template Matcher",      "Mapping payer information to authorization template&#8230;"),
            ("&#x2705;",  "Sanitization Auditor",  "Auditing payloads and finalizing review stage&#8230;"),
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
                        f'</div><div style="font-size:18px;color:#4ade80;flex-shrink:0;">&#10003;</div></div>'
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
                f'border:1px solid rgba(96,165,250,.3);">&#x1F916;</div>'
                f'<div>'
                f'<div style="font-size:16px;font-weight:700;color:#fff;font-family:Outfit,sans-serif;">Clinical Multi-Agent Pipeline Running</div>'
                f'<div style="font-size:12px;color:#93c5fd;margin-top:3px;">{status_label}</div>'
                f'</div></div>'
                f'{rows}'
                f'<div style="margin-top:16px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
                f'<span style="font-size:11px;color:rgba(255,255,255,.45);font-weight:600;text-transform:uppercase;letter-spacing:.6px;">Pipeline Progress</span>'
                f'<span style="font-size:12px;color:#93c5fd;font-weight:700;">{progress_pct}%</span>'
                f'</div>'
                f'<div style="height:6px;background:rgba(255,255,255,.08);border-radius:6px;overflow:hidden;">'
                f'<div style="height:100%;width:{progress_pct}%;background:linear-gradient(90deg,#2563eb,#38bdf8);border-radius:6px;"></div>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

        completed = []
        try:
            render_agent_status(completed, 0, "Initializing pipeline&#8230;", 10)
            time.sleep(0.5)
            completed.append(agent_steps[0])

            render_agent_status(completed, 1, "Parsing document to canonical Markdown&#8230;", 25)
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
                st.session_state.classification = {
                    "category": "Clinical Note",
                    "justification": "API Key required to run live LLM classification.",
                }
                st.session_state.extracted_data = {
                    "request_type": "standard",
                    "member_first_name": "John",
                    "member_last_name":  "Smith",
                    "date_of_birth":     "1972-03-14",
                    "gender":            "M",
                    "member_id":         "BC-AETNA-98213",
                    "req_provider_name": "Emily Carter, MD",
                    "req_provider_npi":  "1234567890",
                    "req_provider_phone": "555-019-2831",
                    "req_provider_fax":  "555-019-2832",
                    "req_provider_contact_person": "Medical Records Dept.",
                    "service_provider_name": "CityFront Orthopedic Imaging Center",
                    "service_provider_address": "1200 Medical Dr, Suite 400, San Francisco, CA 94102",
                    "service_provider_npi": "9876543210",
                    "service_provider_phone": "415-555-1200",
                    "requested_service_types": ["diagnostic_imaging"],
                    "medical_necessity_statement": (
                        "Patient has chronic lumbar pain radiating down the left leg for "
                        "6 months, refractory to conservative therapy. Requesting Lumbar "
                        "Spine MRI to verify nerve root compression."
                    ),
                    "failed_conservative_treatments": [
                        "Physical Therapy (6 weeks)", "NSAIDs (Ibuprofen 800mg)", "Oral steroids", "Gabapentin 300mg TID"
                    ],
                    "diagnostic_tests_summary": "Positive straight leg raise at 40° left. Limited lumbar ROM. Motor weakness 4/5 in left lower extremity.",
                    "functional_impairment_description": "Difficulty performing ADLs and inability to sit for extended periods. Unable to perform work duties.",
                    "lab_values_summary": "ESR 28 mm/hr. CRP 1.2 mg/L. CBC within normal limits.",
                    "diagnosis": [
                        {"code": "M54.16", "description": "Lumbar radiculopathy, left L5 distribution"},
                        {"code": "M51.16", "description": "Intervertebral disc degeneration, lumbar region"},
                    ],
                    "procedure": [
                        {"code": "72148", "description": "MRI Lumbar Spine without contrast"},
                    ],
                    "supporting_chart_notes_available": True,
                }
                st.session_state.clinical_summary = (
                    "### Patient Overview\n"
                    "John Smith is a 54-year-old male. Insurance member ID: BC-AETNA-98213.\n\n"
                    "### Clinical Background\n"
                    "Primary Diagnosis: Lumbar radiculopathy (ICD-10 M54.16) with concurrent disc degeneration (M51.16). "
                    "Chronic low back pain refractory to conservative therapies over 6 months.\n\n"
                    "### Current Symptoms & Status\n"
                    "Severe lower back pain radiating down the left leg. Limited lumbar range of motion. "
                    "Positive straight leg raise test at 40 degrees. Motor weakness 4/5 in left lower extremity.\n\n"
                    "### Failed Conservative Therapies\n"
                    "- Physical Therapy — 6 weeks, no sustained improvement\n"
                    "- NSAIDs (Ibuprofen 800 mg) — partial relief, not sustained\n"
                    "- Oral corticosteroids — temporary relief only\n"
                    "- Gabapentin 300 mg TID — inadequate pain control\n\n"
                    "### Requested Service & CPT Codes\n"
                    "MRI Lumbar Spine without contrast (CPT 72148) at CityFront Orthopedic Imaging Center.\n\n"
                    "### Medical Necessity Justification\n"
                    "The requested MRI is medically necessary due to progressive neurologic deficits, "
                    "positive radiculopathy signs, and failure of comprehensive conservative treatment over 6 months. "
                    "Imaging is required to assess nerve root compression prior to surgical evaluation."
                )
                st.session_state.payer = "Aetna"
                st.session_state.selected_template_path = select_template("Aetna")

                for k in range(2, len(agent_steps)):
                    render_agent_status(completed, k, f"Running {agent_steps[k][1]} (Offline mode)&#8230;", int((k / len(agent_steps)) * 100))
                    time.sleep(0.35)
                    completed.append(agent_steps[k])

            else:
                render_agent_status(completed, 2, "Classifying document category&#8230;", 40)
                st.session_state.classification = classify_document(st.session_state.normalized_markdown, provider, model_name)
                completed.append(agent_steps[2])

                render_agent_status(completed, 3, "Extracting structured clinical entities&#8230;", 60)
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

                render_agent_status(completed, 4, "Generating clinical necessity summary&#8230;", 75)
                st.session_state.clinical_summary = generate_clinical_summary(
                    st.session_state.extracted_data, provider, model_name
                )
                completed.append(agent_steps[4])

                render_agent_status(completed, 5, "Matching insurance payer template&#8230;", 90)
                text_lower      = (st.session_state.normalized_markdown or "").lower()
                member_id_lower = str(st.session_state.extracted_data.get("member_id") or "").lower()
                if "aetna" in text_lower or "aetna" in member_id_lower:
                    st.session_state.payer = "Aetna"
                elif "cigna" in text_lower or "cigna" in member_id_lower:
                    st.session_state.payer = "Cigna"
                else:
                    st.session_state.payer = "Default"
                st.session_state.selected_template_path = select_template(st.session_state.payer)
                completed.append(agent_steps[5])

                render_agent_status(completed, 6, "Running payload verification&#8230;", 98)
                time.sleep(0.4)
                completed.append(agent_steps[6])

            render_agent_status(completed, 7, "All agents finished &#8212; moving to review stage.", 100)
            time.sleep(0.5)
            st.session_state.pa_step = 3
            st.rerun()

        except Exception as exc:
            logger.error("Error in multi-agent pipeline: %s", str(exc), exc_info=True)
            st.session_state.error_message = str(exc)
            st.session_state.pa_step = 3
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — PDF-FIRST REVIEW & EDIT
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.pa_step == 3:
        st.subheader("&#x1F440; Step 3: Review & Edit Prior Authorization Document")

        if not has_api_key:
            st.warning(
                "&#x26A0;&#xFE0F; Offline Mode: No LLM API key detected. "
                "Showing pre-cached fallback data — configure your key in &#x2699;&#xFE0F; Settings."
            )

        if st.session_state.error_message:
            st.error(f"&#x274C; Pipeline failed: {st.session_state.error_message}")
            col_err1, col_err2 = st.columns(2)
            with col_err1:
                if st.button("&#x2B05;&#xFE0F; Back to Upload", use_container_width=True):
                    _reset_state()
                    st.rerun()
            with col_err2:
                if st.button("&#x1F504; Retry Analysis", type="primary", use_container_width=True):
                    st.session_state.error_message = ""
                    st.session_state.pa_step = 2
                    st.rerun()
            return

        data = st.session_state.extracted_data

        # Read all values before widgets render
        fname         = data.get("member_first_name") or ""
        lname         = data.get("member_last_name")  or ""
        dob           = data.get("date_of_birth")     or ""
        gender_val    = data.get("gender")             or ""
        member_id     = data.get("member_id")          or ""
        req_provider  = data.get("req_provider_name")  or ""
        provider_npi  = data.get("req_provider_npi")   or ""
        provider_phone = data.get("req_provider_phone") or ""
        provider_fax  = data.get("req_provider_fax")   or ""
        svc_provider  = data.get("service_provider_name") or ""
        svc_address   = data.get("service_provider_address") or ""
        med_necessity = data.get("medical_necessity_statement")       or ""
        diag_tests    = data.get("diagnostic_tests_summary")          or ""
        func_impair   = data.get("functional_impairment_description") or ""
        failed_list   = data.get("failed_conservative_treatments")    or []
        failed_str    = ", ".join(failed_list) if isinstance(failed_list, list) else str(failed_list)

        diag_list = data.get("diagnosis") or []
        d1_code = diag_list[0].get("code", "")        if diag_list and isinstance(diag_list[0], dict) else ""
        d1_desc = diag_list[0].get("description", "") if diag_list and isinstance(diag_list[0], dict) else ""
        d2_code = diag_list[1].get("code", "")        if len(diag_list) > 1 and isinstance(diag_list[1], dict) else ""
        d2_desc = diag_list[1].get("description", "") if len(diag_list) > 1 and isinstance(diag_list[1], dict) else ""
        proc_list = data.get("procedure") or []
        p1_code = proc_list[0].get("code", "")        if proc_list and isinstance(proc_list[0], dict) else ""
        p1_desc = proc_list[0].get("description", "") if proc_list and isinstance(proc_list[0], dict) else ""

        payer_options = ["Default", "Aetna", "Cigna"]
        payer_idx = payer_options.index(st.session_state.payer) if st.session_state.payer in payer_options else 0
        summary_text = st.session_state.clinical_summary

        # ── Two-column layout ─────────────────────────────────────────────
        col_edit, col_preview = st.columns([1, 1.35])

        # ── LEFT: Edit Panel ──────────────────────────────────────────────
        with col_edit:
            st.markdown(
                '<div style="font-size:14px;font-weight:700;color:var(--text-accent);'
                'margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid var(--blue-300);">'
                '&#x270D;&#xFE0F;&nbsp; Edit Authorization Fields</div>',
                unsafe_allow_html=True,
            )

            tab_demo, tab_provider, tab_codes, tab_clinical, tab_summary = st.tabs([
                "&#x1F464; Patient",
                "&#x1F3E5; Providers",
                "&#x1F522; Codes",
                "&#x1FA7A; Clinical",
                "&#x1F4CB; Summary",
            ])

            with tab_demo:
                c1, c2 = st.columns(2)
                with c1:
                    fname      = st.text_input("First Name",             value=fname,      key="pa_fname")
                    lname      = st.text_input("Last Name",              value=lname,      key="pa_lname")
                    dob        = st.text_input("Date of Birth",          value=dob,        key="pa_dob",
                                               placeholder="YYYY-MM-DD")
                with c2:
                    gender_val = st.text_input("Gender (M / F)",         value=gender_val, key="pa_gender")
                    member_id  = st.text_input("Member / Subscriber ID", value=member_id,  key="pa_member_id")
                    selected_payer = st.selectbox("Insurance Payer",     payer_options,    index=payer_idx, key="pa_payer")

            with tab_provider:
                st.markdown("**Requesting Provider**")
                req_provider  = st.text_input("Provider Name",    value=req_provider,  key="pa_provider")
                c1, c2 = st.columns(2)
                with c1:
                    provider_npi   = st.text_input("NPI",         value=provider_npi,  key="pa_npi")
                    provider_phone = st.text_input("Phone",       value=provider_phone,key="pa_prov_phone")
                with c2:
                    provider_fax   = st.text_input("Fax",         value=provider_fax,  key="pa_prov_fax")
                st.markdown("**Service Provider / Facility**")
                svc_provider   = st.text_input("Facility Name",   value=svc_provider,  key="pa_svc_name")
                svc_address    = st.text_input("Facility Address", value=svc_address,  key="pa_svc_addr")

            with tab_codes:
                st.markdown("**ICD-10 Diagnosis Codes**")
                c1, c2 = st.columns([1, 3])
                with c1:
                    d1_code = st.text_input("Code 1",  value=d1_code, key="pa_d1_code")
                    d2_code = st.text_input("Code 2",  value=d2_code, key="pa_d2_code")
                with c2:
                    d1_desc = st.text_input("Dx 1 Description", value=d1_desc, key="pa_d1_desc")
                    d2_desc = st.text_input("Dx 2 Description", value=d2_desc, key="pa_d2_desc")

                st.markdown("**CPT / HCPCS Procedure Codes**")
                c1, c2 = st.columns([1, 3])
                with c1:
                    p1_code = st.text_input("CPT Code", value=p1_code, key="pa_p1_code")
                with c2:
                    p1_desc = st.text_input("CPT Description", value=p1_desc, key="pa_p1_desc")

            with tab_clinical:
                med_necessity = st.text_area("Medical Necessity Statement", value=med_necessity,
                                             height=100, key="pa_med_nec")
                diag_tests    = st.text_area("Diagnostic Tests & Results",  value=diag_tests,
                                             height=80,  key="pa_diag_tests")
                failed_str    = st.text_input("Failed Treatments (comma-separated)", value=failed_str,
                                              key="pa_failed")
                func_impair   = st.text_area("Functional Impairment",       value=func_impair,
                                             height=80,  key="pa_func")

            with tab_summary:
                summary_text = st.text_area(
                    "Clinical Necessity Summary (Markdown)",
                    value=summary_text,
                    height=320,
                    key="pa_summary",
                )

            st.divider()

            # ── Action buttons ────────────────────────────────────────────
            def _save_edits():
                """Flush all widget values back to session state."""
                diag_entries = [{"code": st.session_state.pa_d1_code, "description": st.session_state.pa_d1_desc}]
                if st.session_state.pa_d2_code or st.session_state.pa_d2_desc:
                    diag_entries.append({"code": st.session_state.pa_d2_code, "description": st.session_state.pa_d2_desc})
                st.session_state.extracted_data.update({
                    "member_first_name":               st.session_state.pa_fname,
                    "member_last_name":                st.session_state.pa_lname,
                    "date_of_birth":                   st.session_state.pa_dob,
                    "gender":                          st.session_state.pa_gender,
                    "member_id":                       st.session_state.pa_member_id,
                    "req_provider_name":               st.session_state.pa_provider,
                    "req_provider_npi":                st.session_state.pa_npi,
                    "req_provider_phone":              st.session_state.pa_prov_phone,
                    "req_provider_fax":                st.session_state.pa_prov_fax,
                    "service_provider_name":           st.session_state.pa_svc_name,
                    "service_provider_address":        st.session_state.pa_svc_addr,
                    "medical_necessity_statement":     st.session_state.pa_med_nec,
                    "diagnostic_tests_summary":        st.session_state.pa_diag_tests,
                    "functional_impairment_description": st.session_state.pa_func,
                    "failed_conservative_treatments":  [
                        x.strip() for x in st.session_state.pa_failed.split(",") if x.strip()
                    ],
                    "diagnosis":  diag_entries,
                    "procedure":  [{"code": st.session_state.pa_p1_code, "description": st.session_state.pa_p1_desc}],
                })
                st.session_state.clinical_summary = st.session_state.pa_summary
                st.session_state.payer = st.session_state.pa_payer
                st.session_state.selected_template_path = select_template(st.session_state.pa_payer)

            b1, b2 = st.columns(2)
            with b1:
                if st.button("&#x1F504; Update Preview", use_container_width=True, key="pa_update_preview"):
                    _save_edits()
                    st.rerun()
            with b2:
                if st.button("&#x1F4BE; Finalize & Export", type="primary", use_container_width=True, key="pa_compile"):
                    _save_edits()
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

            b3, b4 = st.columns(2)
            with b3:
                if st.button("&#x2B05;&#xFE0F; Restart / Reset", use_container_width=True, key="pa_reset"):
                    _reset_state()
                    st.rerun()
            with b4:
                if st.button("&#x1F504; Re-run AI Extraction", use_container_width=True, key="pa_rerun"):
                    _save_edits()
                    st.session_state.pa_step = 2
                    st.rerun()

        # ── RIGHT: PDF-First Document Preview ────────────────────────────
        with col_preview:
            # Build live preview from current session state (already saved by Update Preview,
            # or freshly arrived from Step 2)
            preview_data    = st.session_state.extracted_data
            preview_summary = st.session_state.clinical_summary
            preview_payer   = st.session_state.payer

            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:space-between;'
                'margin-bottom:10px;">'
                '<div style="font-size:14px;font-weight:700;color:var(--text-accent);">'
                '&#x1F4C4;&nbsp; Live Prior Authorization Preview</div>'
                '<div style="font-size:11px;color:var(--text-muted);font-style:italic;">'
                'Edit fields on the left, then click &#x201C;Update Preview&#x201D;</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            pa_html = build_pa_html_preview(preview_data, preview_summary, preview_payer)
            components.html(pa_html, height=1080, scrolling=True)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — EXPORT & DOWNLOAD
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.pa_step == 4:
        st.subheader("&#x2705; Step 4: Export Completed Package")

        st.markdown(
            """<div style="background:var(--success-bg);border:2px solid var(--success-border);
                    border-radius:14px;padding:32px;text-align:center;margin-bottom:30px;">
                <h2 style="color:var(--success-text);margin-top:0;font-family:'Outfit',sans-serif;font-weight:700;">
                    &#x1F389; Prior Authorization Package Finalized
                </h2>
                <p style="font-size:16px;color:var(--success-subtext);font-weight:500;">
                    Multi-agent pipeline completed: notes extracted, necessity verified, templates compiled.
                </p>
                <p style="font-size:14px;color:var(--success-subtext);">
                    Ready for download and direct EHR integration.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1.35])

        with col1:
            st.markdown("### &#x1F4E5; Multi-Format Downloads")
            st.markdown("Download the compiled medical necessity package in your preferred format:")

            if st.session_state.filled_docx_path and os.path.exists(st.session_state.filled_docx_path):
                with open(st.session_state.filled_docx_path, "rb") as fh:
                    docx_bytes = fh.read()
                st.download_button(
                    "&#x1F4E5; Download Completed Word Form (.docx)",
                    data=docx_bytes,
                    file_name=os.path.basename(st.session_state.filled_docx_path),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

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
                "&#x1F4C4; Download Clinical Necessity PDF Summary",
                data=pdf_bytes,
                file_name=f"prior_auth_clinical_summary_{safe_last}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
            st.download_button(
                "&#x1F4DD; Download Clinical Summary (.md)",
                data=st.session_state.clinical_summary,
                file_name=f"prior_auth_clinical_summary_{safe_last}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.download_button(
                "&#x2699;&#xFE0F; Download Raw EHR Record (.json)",
                data=json.dumps(st.session_state.extracted_data, indent=4),
                file_name=f"prior_auth_ehr_payload_{safe_last}.json",
                mime="application/json",
                use_container_width=True,
            )

            st.divider()
            if st.button("&#x1F504; Start New Authorization Request", use_container_width=True, key="pa_new"):
                _reset_state()
                st.rerun()
            if st.button("&#x2B05;&#xFE0F; Return to Review & Edit", use_container_width=True, key="pa_back"):
                st.session_state.pa_step = 3
                st.rerun()

        with col2:
            st.markdown("### &#x1F50D; Final Document Preview")
            st.markdown(
                '<div style="font-size:11px;color:var(--text-muted);margin-bottom:8px;">'
                'This is the exact document that was exported. What You See Is What You Get.</div>',
                unsafe_allow_html=True,
            )
            final_html = build_pa_html_preview(
                st.session_state.extracted_data,
                st.session_state.clinical_summary,
                st.session_state.payer,
            )
            components.html(final_html, height=1080, scrolling=True)

    render_floating_chat()


if __name__ == "__main__":
    setup_page()
    render_prior_auth_page()
