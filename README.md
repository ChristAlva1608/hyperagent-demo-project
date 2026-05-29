# Streamlit & LangChain AI Application Template

A clean, modern boilerplate for building agentic and AI-powered chat interfaces using the **Streamlit** front-end framework and the **LangChain** logic framework. It leverages modern Python tooling featuring `pyproject.toml` and `uv` lock files for lightning-fast and reproducible environment setups.

---

## 🏗️ Folder Structure

The project has been architected with modularity and separation of concerns in mind:

```
hyperagent-demo-project/
├── pyproject.toml              # Modern Python dependency specifications
├── uv.lock                     # Lightning-fast locked dependency tree
├── Makefile                    # Standard orchestration commands (setup, run, clean...)
├── .env.example                # Configuration parameters template
├── README.md                   # You are here!
├── .gitignore                  # Robust ignore list for Python & Streamlit
│
└── app/                        # Main application package
    ├── __init__.py
    ├── main.py                 # Streamlit application main entrance page
    ├── config.py               # Application configurations & dotenv parser
    │
    ├── pages/                  # Streamlit Multi-page structure
    │   ├── __init__.py
    │   └── chat.py             # Chat application showcasing LangChain LCEL
    │
    ├── components/             # Reusable UI components
    │   ├── __init__.py
    │   └── sidebar.py          # Shared sidebar for settings (Model select, keys, temperature)
    │
    ├── chains/                 # LangChain LCEL chains & complex logic
    │   ├── __init__.py
    │   └── chat_chain.py       # Custom chat assistant logic pipeline
    │
    ├── models/                 # Model factories & instantiation
    │   ├── __init__.py
    │   └── llm.py              # LLM wrapper factory
    │
    ├── handlers/               # LangChain custom event & callback handlers
    │   ├── __init__.py
    │   └── stream_handler.py   # Streaming callback handler feeding UI containers
    │
    ├── prompts/                # Chat system, context and prompt templates
    │   ├── __init__.py
    │   └── templates.py        # System prompts and prompt builders
    │
    └── utils/                  # Application utility modules
        ├── __init__.py
        └── helpers.py          # Helper functions (API key checker, chat resets)
```

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have `make` installed on your machine. The boilerplate uses `uv` for package management. The application setup will automatically download and install `uv` if it is missing.

### 2. Launch the Application
Simply run the following command in your terminal:
```bash
make run
```
This single command automatically handles the end-to-end setup process, including:
1. Creating a local `.env` file from the `.env.example` template (if not already present).
2. Installing/verifying the `uv` package manager.
3. Syncing all project dependencies.
4. Launching the Streamlit application interface.

Your default browser will launch, pointing to `http://localhost:8501`.

### 3. Configure API Credentials (Secure Backend Model)
To ensure compliance and data security, API keys are never entered in the browser UI. Instead, keys are loaded strictly from backend environment variables.

Open the root `.env` file and append the credentials for the AI providers you want to activate:

```env
# 1. OpenAI (ChatGPT)
OPENAI_API_KEY=your_openai_key_here

# 2. DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key_here

# 3. Google Gemini
GEMINI_API_KEY=your_gemini_key_here
```

When you start the application, the settings sidebar will automatically verify the presence of these environment parameters and display a secure `🔒 Connected` badge for the selected provider.

---

## 🛠️ Makefile Commands

| Command | Action |
| :--- | :--- |
| `make run` | Setup environment (bootstrap `uv` + sync dependencies) and run the Streamlit app |
| `make lock` | Re-generate the dependency locking tree (`uv.lock`) |
| `make clean` | Clean runtime, ruff, and `__pycache__` artifacts |

---

## 💡 Customization Guide

1. **System Prompt**: Alter how the assistant behaves by modifying the system prompt text in `app/prompts/templates.py`.
2. **Chain Pipeline**: Enhance logic chains or create advanced retrieval pipelines (RAG) by adjusting `app/chains/chat_chain.py`.
3. **Sidebar Controls**: Add sliders, input fields, or selectors to the sidebar in `app/components/sidebar.py`.
4. **Additional Pages**: Streamlit dynamically picks up any script added inside the `app/pages/` folder. Add pages like `data_visualizer.py` or `settings.py` here.