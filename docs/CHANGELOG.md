# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-05-30

### ✨ Added

#### Prior Authorization Workflow Redesign
- **`app/pages/2_📋_Prior_Authorization.py`** — Complete 4-step workflow overhaul:
  - Step 1: Unified file uploader accepting PDF, DOCX, TXT, PNG, JPG, JPEG with live document preview and one-click sample note loader
  - Step 2: Real multi-agent pipeline with animated glass overlay (Pipeline Router → Ingestion → Classification → Extraction → Summary → Template Matcher → Auditor)
  - Step 3: Two-column interactive clinician portal with tabbed edit forms (Demographics, Clinical Evidence, CPT/ICD Codes, Medical Summary)
  - Step 4: Multi-format export panel (DOCX, PDF, Markdown, JSON)
- **`app/utils/prior_auth_agents.py`** — New module housing four AI agent functions:
  - `classify_document()` — LLM-based clinical document classifier (Clinical Note, Lab Report, Imaging Report, etc.)
  - `extract_medical_info()` — Structured extraction via existing `prior_auth_handler` Pydantic pipeline
  - `generate_clinical_summary()` — Medical necessity justification summary generator
  - `select_template()` — Dynamic payer-to-template mapper (Aetna, Cigna, Default)
- **`app/utils/text_to_pdf.py`** — Pure-Python PDF byte stream generator with no external binary dependencies. Handles word-wrap, bold headers (`#`, `##`, `###`), and bullet lists across multiple pages.
- **`app/data/templates/aetna_prior_authorization_template.docx`** — Aetna-specific PA form template
- **`app/data/templates/cigna_prior_authorization_template.docx`** — Cigna-specific PA form template
- **`docs/PRIOR_AUTH_REDESIGN.md`** — Full technical deep-dive of the redesign architecture
- **`docs/CHANGELOG.md`** — This file

### 🔧 Changed

- **`app/utils/processing_file.py`** — Extension validation now runs *before* file-bytes check, ensuring unsupported formats raise `ValueError: Unsupported file format` rather than `Could not read content` — fixes test assertion in `test_unsupported_extension`.
- **`app/pages/2_📋_Prior_Authorization.py`** — Replaced old single-call OCR pipeline with full multi-agent sequential execution. Supports offline fallback mode with pre-cached clinical presets when no API key is configured.

### 🐛 Fixed

- **`app/utils/prior_auth_agents.py`** — `extract_medical_info` import of `prior_auth_handler` wrapped in `try/except ImportError` to handle both `app.handlers.*` and `handlers.*` module resolution depending on Python runtime working directory.
- **`app/pages/2_📋_Prior_Authorization.py`**:
  - Removed dead imports (`APP_TITLE`, `base64`, `get_llm`, `get_provider_api_key`) that were imported but never used.
  - Fixed `proc1_desc` self-reference bug: widget previously used its own output variable as its `value=` argument instead of the raw `p1_desc` extracted from session data.
  - Fixed `NameError` on Compile button: form field variables (`fname`, `lname`, `diag1_code`, `proc1_code`, etc.) were previously declared only *inside* tab blocks. Since Streamlit only executes the active tab, variables from inactive tabs were undefined when the button fired. Fixed by reading all values from session state keys directly inside the button handler.
  - Fixed missing `selected_template_path` in offline fallback: template was never set in no-API-key branch, causing `fill_template_docx` to receive an empty path.
  - Fixed heading capitalisation: `"normalized Patient records"` → `"Normalised Patient Record"`.
  - Extracted repeated reset logic into a shared `_reset_state()` helper.

### 🧪 Tests

- **`tests/test_prior_auth.py`**:
  - `test_unsupported_extension`: changed test input from `test.txt` (now a supported format) to `test.xyz`
  - `test_text_to_pdf` (new): verifies `text_to_pdf()` returns valid `bytes` starting with `%PDF` and ending with `%%EOF`
  - All **7 tests** pass (`Ran 7 tests in ~4s — OK`)

---

## Previous Sessions

### Bug Fixes & Improvements (earlier sessions)

#### 🔑 API Key Validation
- Rewrote key validation in `app/utils/api_key_validator.py` to accept any key ≥ 8 chars that is not a placeholder string, supporting enterprise proxies and non-standard key formats.
- Updated `.env` and `.env.example` to include proper variable names for OpenAI, DeepSeek, Gemini, and Google.

#### 💬 Floating Chat
- Fixed `StreamlitAPIException`: `st.session_state.f_chat_uploaded_file` cannot be modified after widget instantiation — replaced direct session state assignment with a clear-flag pattern.
- Added file upload support to the floating chat panel.

#### 🤖 Chat Assistant
- Fixed verbosity issue: chat assistant returned extremely long responses to simple greetings (`hi`, `hello`) because the old system prompt instructed the model to explain why questions were incoherent.
- Refactored `SYSTEM_PROMPT` in `app/prompts/templates.py` to a concise clinical persona.
- Fixed `ModuleNotFoundError: No module named 'prompts.templates'` caused by a stale import path after module rename.

#### 📋 Prior Authorization (pre-redesign)
- Removed synthetic mock data constants (`MOCK_EXTRACTED_TEXT`, `MOCK_INSURANCE_FORM`) from Step 3 preview.
- Added explicit three-state rendering: Success, No-Key warning, Error detail.
