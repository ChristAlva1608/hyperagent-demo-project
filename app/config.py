import os
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# App configurations
APP_TITLE = os.getenv("APP_TITLE", "AI Assistant Template")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

# LangChain Settings
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "streamlit-langchain-template")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def validate_config():
    """Verify minimum required configurations are set."""
    warnings = []
    if not OPENAI_API_KEY:
        warnings.append("OPENAI_API_KEY is not set. OpenAI models will fail to load unless provided dynamically.")
    return warnings