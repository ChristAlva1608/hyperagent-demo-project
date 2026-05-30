# Prior Authorization Workflow Redesign
## Technical Architecture & Implementation Guide

This document is the authoritative technical reference for the complete redesign of the Prior Authorization module (`app/pages/2_📋_Prior_Authorization.py`) delivered on 2026-05-30. It covers architecture decisions, data flow, module contracts, and known constraints.

---

## 1. Objective

Convert the original single-pass OCR pipeline (image upload → LLM text extraction → static Markdown form) into a scalable, AI-driven, human-in-the-loop clinical workflow that:

1. Accepts **any document format** (PDF, DOCX, TXT, scanned images)
2. **Normalises all inputs** to clean Markdown before any AI processing
3. Runs a **sequential multi-agent pipeline** for classification, structured extraction, and clinical summary generation
4. **Dynamically selects** the correct payer template (Aetna, Cigna, or Default)
5. Allows a **clinician to review and edit** every extracted field before finalization
6. Exports the completed package as **DOCX + PDF + Markdown + JSON**

---

## 2. Module Map

```
app/
├── pages/
│   └── 2_📋_Prior_Authorization.py   ← Orchestrator (UI + step router)
├── utils/
│   ├── processing_file.py            ← Unified ingestion → Markdown normaliser
│   ├── prior_auth_agents.py          ← Four AI agent functions
│   ├── fill_template_docx.py         ← DOCX template filler (placeholder engine)
│   ├── fille_template_pdf.py         ← PDF form field filler (pypdf)
│   └── text_to_pdf.py                ← Pure-Python Markdown → PDF byte stream
├── handlers/
│   └── prior_auth_handler.py         ← Pydantic extraction chain (reused)
├── models/
│   └── prior_auth_model.py           ← Dynamic Pydantic model factory
├── data/
│   ├── extracted_fields.json         ← 30-field extraction schema
│   ├── templates/
│   │   ├── aetna_prior_authorization_template.docx
│   │   ├── cigna_prior_authorization_template.docx
│   │   └── prior_authorization_template.docx
│   ├── patient_notes/
│   │   └── sample_patient_note_prior_authorization.docx
│   └── output/                       ← Runtime-generated filled documents
```

---

## 3. Step-by-Step Data Flow

### Step 1 — Load Document

```
User uploads file  ──►  st.file_uploader (PDF/DOCX/TXT/PNG/JPG/JPEG)
                         │
                         ▼
               st.session_state.uploaded_file_bytes
               st.session_state.uploaded_file_name
```

**Or** user clicks **Load Sample Record** → reads `data/patient_notes/sample_patient_note_prior_authorization.docx` from disk.

### Step 2 — Multi-Agent Pipeline

```
FileMock(name, getvalue)
        │
        ▼
 processing_file(file_mock)
        │  Dispatches by extension:
        │  .txt  → decode UTF-8
        │  .docx → docx2txt
        │  .pdf  → pypdf digital extract; if sparse → pdf2image + OCR
        │  .png/.jpg/.jpeg → PIL Image + LLM vision OCR
        ▼
  normalized_markdown  ──────────────────────────────────────────┐
        │                                                         │
        ▼                                                         │
 classify_document(markdown, provider, model)                     │
        │  SystemMessage: category classifier                     │
        │  Returns: {category, justification}                     │
        ▼                                                         │
 extract_medical_info(markdown, fields, provider, model)          │
        │  Delegates to prior_auth_handler (Pydantic chain)       │
        │  fields loaded from data/extracted_fields.json          │
        │  Returns: model.model_dump() → Dict[str, Any]           │
        ▼                                                         │
 generate_clinical_summary(extracted_data, provider, model)       │
        │  6-section structured Markdown report                   │
        │  Returns: str (Markdown)                                │
        ▼                                                         │
 select_template(payer)                                           │
        │  "aetna" → aetna_prior_authorization_template.docx      │
        │  "cigna" → cigna_prior_authorization_template.docx      │
        │  else   → prior_authorization_template.docx             │
        ▼                                                         │
 All results stored in st.session_state ◄────────────────────────┘
 pa_step = 3 → st.rerun()
```

**Offline fallback** (no API key): Steps 3–7 are skipped; pre-cached clinical preset data is loaded directly into session state, including a hardcoded `selected_template_path = select_template("Aetna")`.

### Step 3 — Clinician Review

```
st.session_state.extracted_data
        │
        ▼  Values read into local vars BEFORE tabs render
   fname, lname, dob, gender, member_id,
   req_provider, provider_npi,
   med_necessity, diag_tests, failed_str, func_impair,
   d1_code, d1_desc, p1_code, p1_desc,
   payer_idx, summary_text
        │
        ▼  Rendered in 4 tabs with unique widget keys (pa_fname, pa_lname…)
   tab_demo | tab_clinical | tab_codes | tab_summary
        │
        ▼  On "Compile & Finalize" button:
   Read all values from st.session_state.<key>
   → update extracted_data dict
   → select_template(pa_payer)
   → fill_template_docx(template_path, extracted_data, output_path)
   → pa_step = 4
```

> **Critical design note**: All editable field *initial values* are pulled from `st.session_state.extracted_data` **before** the tab widgets render. The Compile handler reads back from `st.session_state.<widget_key>` rather than local variables. This prevents `NameError` when the active tab differs from the tab where a variable was declared.

### Step 4 — Export Package

| Download | Source | Method |
|----------|--------|--------|
| `.docx` | `data/output/filled_prior_auth_<lastname>.docx` | `fill_template_docx()` called in Step 3 |
| `.pdf` | Generated at download time | `text_to_pdf(clinical_summary, title)` |
| `.md` | `st.session_state.clinical_summary` | Direct string download |
| `.json` | `st.session_state.extracted_data` | `json.dumps(indent=4)` |

---

## 4. Agent Contracts

### `classify_document(markdown_text, provider, model_name) → Dict`

| Field | Type | Description |
|-------|------|-------------|
| `category` | `str` | One of: Clinical Note, Progress Note, Lab Report, Imaging Report, Referral, Insurance Document, Supporting Evidence |
| `justification` | `str` | One-sentence clinical reason |

- Uses `temperature=0.0` for deterministic output
- Parses LLM response as JSON, stripping ` ```json ` fences
- Fails gracefully: returns `{"category": "Clinical Note", "justification": "Failed to classify: <error>"}` on any exception

### `extract_medical_info(markdown_text, fields, provider, model_name) → Dict`

- Delegates entirely to `prior_auth_handler(uploaded_file=None, content=markdown_text, fields=fields, …)`
- Returns `result_model.model_dump()` — a flat-ish dict matching the 30 fields in `extracted_fields.json`
- Import resolved via `try/except ImportError` for `app.handlers` vs `handlers` path

### `generate_clinical_summary(extracted_data, provider, model_name) → str`

- Uses `temperature=0.3`
- System prompt enforces six Markdown headers: Patient Overview, Clinical Background, Current Symptoms, Failed Therapies, Requested Service, Medical Necessity Justification
- Returns raw Markdown string
- Fails gracefully: returns a `### ⚠️ Summary Generation Error` Markdown block

### `select_template(payer) → str`

- Case-insensitive substring match: `"aetna"` in payer → Aetna template
- Returns absolute path to template file
- Falls back to `prior_authorization_template.docx` if payer-specific file missing

---

## 5. Extraction Schema

Defined in `app/data/extracted_fields.json` (30 fields). Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `member_first_name` / `member_last_name` | `str` | Patient name |
| `member_id` | `str` | Insurance subscriber ID |
| `date_of_birth` | `str` | YYYY-MM-DD |
| `gender` | `str` | `M` or `F` |
| `req_provider_name` / `req_provider_npi` | `str` | Requesting physician |
| `diagnosis` | `list[{code, description}]` | ICD-10 codes |
| `procedure` | `list[{code, description}]` | CPT / HCPCS codes |
| `failed_conservative_treatments` | `list[str]` | Prior therapy failures |
| `medical_necessity_statement` | `str` | Clinical justification |
| `diagnostic_tests_summary` | `str` | MRI / CT / lab findings |
| `functional_impairment_description` | `str` | ADL impact statement |

---

## 6. PDF Generator (`text_to_pdf`)

`app/utils/text_to_pdf.py` is a zero-dependency, pure-Python PDF 1.4 byte stream generator.

**Supported Markdown syntax:**

| Input | Rendering |
|-------|-----------|
| `# Heading` | Helvetica-Bold 16 pt |
| `## Heading` | Helvetica-Bold 14 pt |
| `### Heading` | Helvetica-Bold 12 pt |
| `- item` / `* item` | Bullet line, Helvetica 11 pt |
| Plain text | Helvetica 11 pt, word-wrapped at 85 chars |

**Page properties:** A4 portrait (595 × 842 pt), 50 pt left margin, 14 pt line height, automatic page breaks at Y < 60 pt.

---

## 7. Known Constraints & Next Steps

### Current Limitations

| Constraint | Detail |
|------------|--------|
| Single ICD-10 row in UI | Step 3 only renders row 1 of the `diagnosis` list. Multi-diagnosis editing requires dynamic `st.data_editor` or repeated widget blocks. |
| Single CPT row in UI | Same as above for `procedure` list. |
| `time.sleep()` in Step 2 | Synchronous delays block the Streamlit thread during agent animation; consider `st.status` or async execution in future. |
| PDF emoji rendering | Pure-Python PDF generator uses Helvetica which lacks emoji glyphs; emojis in clinical summary headers are stripped or rendered as `?`. |
| Scanned PDF OCR cost | Each page of a scanned PDF triggers a separate vision LLM call — large documents will consume significant token quota. |

### Recommended Next Steps

1. **Multi-row ICD/CPT editing**: Replace single text inputs with `st.data_editor` bound to `diagnosis` and `procedure` lists.
2. **Async agent execution**: Wrap agent calls in `asyncio.gather()` where order allows, reducing total Step 2 wall-clock time.
3. **Emoji-safe PDF**: Replace Helvetica with a Unicode-capable font (e.g. embed DejaVu Sans subset) or strip emojis before PDF rendering.
4. **Direct EHR submission**: Add a "Submit to EHR" action in Step 4 that POSTs the JSON payload to a configured FHIR endpoint.
5. **Audit trail**: Log every agent invocation (input hash, model, output) to a local SQLite table for HIPAA-compliant traceability.
