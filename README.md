# Streamlit & LangChain Clinical AI Platform

A clean, modular, and high-fidelity clinical assistant platform built using the **Streamlit** front-end framework and the **LangChain** logic framework. This repository features an advanced multi-agent Prior Authorization workflow, an AI chat assistant, a floating clinical co-pilot, and robust configuration panels. It leverages modern Python tooling featuring `pyproject.toml` and `uv` lock files for fast, reproducible environment setups.

---

## 🏗️ Folder Structure

The project has been architected with modularity, separation of concerns, and robust package-level initialization in mind:

```
hyperagent-demo-project/
├── pyproject.toml              # Modern Python dependency specifications
├── uv.lock                     # Locked dependency tree
├── Makefile                    # Orchestration commands (setup, run, clean...)
├── .env.example                # Configuration parameters template
├── README.md                   # You are here!
├── .gitignore                  # Ignore list for Python & Streamlit
├── tests/                      # Project test suite (7 comprehensive test cases)
│   ├── test_fill_docx.py       # DOCX template fill tests
│   └── test_prior_auth.py      # Prior auth ingestion and parser tests
│
└── app/                        # Main application package
    ├── __init__.py             # Entry initialization (handles path resolution, config, and logging)
    ├── 🏥_Clinical_Hub.py      # Clinical Hub Dashboard (main landing page)
    ├── config.py               # Application configuration loader and basic logging setup
    │
    ├── pages/                  # Streamlit Multi-page structure
    │   ├── 1_💬_Chat_Assistant.py      # AI Clinical Assistant interface
    │   ├── 2_📋_Prior_Authorization.py # Sequential Multi-Agent Prior Auth Redesign
    │   └── 3_⚙️_Settings.py            # Global provider and credential manager
    │
    ├── components/             # Reusable UI components
    │   ├── chat.py             # Chat messaging interface
    │   ├── floating_chat.py    # Floating clinical co-pilot overlay
    │   └── floating_settings.py# Floating assistant settings popover
    │
    ├── chains/                 # LangChain LCEL workflows
    │   └── chat_chain.py       # Conversational agent and tools pipeline
    │
    ├── models/                 # Model factories & validation schemas
    │   ├── llm.py              # Dynamic LLM wrapper (OpenAI, Gemini, DeepSeek)
    │   └── prior_auth_model.py # Dynamic Pydantic schema validation model
    │
    ├── handlers/               # Event & callback handlers
    │   ├── prior_auth_handler.py# Pydantic extraction chain handler
    │   └── stream_handler.py   # Streaming callback handler feeding UI containers
    │
    ├── prompts/                # Chat system, context and prompt templates
    │   └── templates.py        # System clinical assistant prompt builders
    │
    └── utils/                  # Application utility modules
        ├── api_key_validator.py# Key validator accepting standard & proxy API keys
        ├── fill_template_docx.py# Word document template compiler
        ├── prior_auth_agents.py# Sequential multi-agent pipeline steps
        ├── processing_file.py  # OCR, PDF/Word/Image ingestion & MD normalizer
        ├── text_to_pdf.py      # Zero-dependency, pure-Python Markdown-to-PDF compiler
        └── theme.py            # Clinical stylesheets & custom dark mode theme injection
```

---

## 🌟 Key Features

### 1. Sequential Multi-Agent Prior Authorization Workflow
Located under `app/pages/2_📋_Prior_Authorization.py`, this is a 4-step clinician portal:
- **Step 1: Ingest Record**: A unified file uploader accepting PDFs, Word Documents (`.docx`), scanned/plain text files, and images (`.png`, `.jpg`, `.jpeg`). Features a one-click sample loader.
- **Step 2: Analysis Pipeline**: Runs a multi-agent sequential pipeline:
  - **Pipeline Router & Ingestion**: Converts uploaded bytes into structured Markdown text (utilizing Vision LLM OCR for images and sparse PDFs).
  - **Classification Agent**: Categorizes the document type (e.g., Clinical Note, Lab Report) with clinical justification.
  - **Extraction Agent**: Extracts 30 essential prior authorization fields matching standard clinical criteria.
  - **Summary Agent**: Compiles a 6-section medical necessity justification.
  - **Template Matcher**: Dynamically maps the carrier (Aetna, Cigna, or Default) to corresponding Word templates.
- **Step 3: Review & Preview**: A two-column interactive portal. The left column organizes the 30 extracted fields into editable tabs (Demographics, Clinical Evidence, CPT/ICD Codes, and Medical Summary). The right column shows a live PDF-first rendering of the filled Aetna/Cigna document.
- **Step 4: Final Package**: Generates multi-format download packages including DOCX, PDF, Markdown, and JSON.

### 2. Zero-Dependency PDF Compiler (`text_to_pdf`)
A pure-Python PDF 1.4 byte stream generator designed to avoid external binary dependencies. It dynamically parses structured Markdown headers (`#`, `##`, `###`), bullets (`-`, `*`), and text to compile an A4 PDF document with multi-page support.

### 3. Modular Path Resolution and Package Initialization
The packages use specialized `__init__.py` files to expose clean APIs, automatically load global configurations and `.env` variables on package load, and dynamically configure `sys.path` to eliminate importing issues.

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have `make` installed. The platform uses `uv` for package management. The application setup will automatically download and install `uv` if it is missing.

### 2. Launch the Application
Run the following command in your terminal:
```bash
make run
```
This command automatically handles the end-to-end setup:
1. Creates a local `.env` file from the `.env.example` template (if not already present).
2. Installs/verifies the `uv` package manager.
3. Syncing all project dependencies.
4. Launches the Streamlit application interface.

The application runs on `http://localhost:8080`.

### 3. Add API Credentials
To utilize the AI Chat assistant and Prior Authorization features:
- Configure your credentials in the global settings page under **`app/pages/3_⚙️_Settings.py`** in the application interface.
- **Or** fill in your API Keys inside the `.env` file:
  ```env
  OPENAI_API_KEY=your_key_here
  DEEPSEEK_API_KEY=your_key_here
  GEMINI_API_KEY=your_key_here
  ```

---

## 🛠️ Orchestration Commands

| Command | Action |
| :--- | :--- |
| `make run` | Setup environment (bootstrap `uv` + sync dependencies) and run the Streamlit app on port 8080 |
| `make lock` | Re-generate the dependency locking tree (`uv.lock`) |
| `make clean` | Clean runtime, ruff, and `__pycache__` cache artifacts |
| `uv run python -m unittest discover tests` | Run the complete project test suite |

---

## 💡 Customization Guide

1. **System Prompt**: Alter the clinical assistant's behavior by modifying the system prompt text in `app/prompts/templates.py`.
2. **Chain Pipeline**: Enhance agentic logic chains or build advanced retrieval pipelines (RAG) by adjusting `app/chains/chat_chain.py`.
3. **Global Settings**: Customize model parameters, API key inputs, and settings logic in the global panel under `app/pages/3_⚙️_Settings.py`.
4. **Additional Pages**: Streamlit dynamically picks up any script added inside the `app/pages/` folder. Add pages like `data_visualizer.py` or similar scripts here.