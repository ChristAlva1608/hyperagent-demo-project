import os
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# App configurations
APP_TITLE = os.getenv("APP_TITLE", "AI Assistant Template")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

# Model Provider and Model Routing (Configured Secretly)
ACTIVE_PROVIDER = os.getenv("ACTIVE_PROVIDER", "OpenAI")
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "gpt-4o-mini")
ACTIVE_TEMPERATURE = float(os.getenv("ACTIVE_TEMPERATURE", "0.7"))

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def validate_config():
    """Verify minimum required configurations are set for the active provider."""
    warnings = []
    
    # Import inside function to prevent circular imports
    from utils.helpers import check_provider_api_key
    
    if not check_provider_api_key(ACTIVE_PROVIDER):
        warnings.append(f"API Credentials for the active provider '{ACTIVE_PROVIDER}' are missing in your backend environment.")
        
    return warnings