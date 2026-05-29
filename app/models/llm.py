from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config import DEFAULT_MODEL, SUPPORTED_MODELS

def _get_provider(model_name: str) -> str:
    """Helper to detect provider based on the model name."""
    for provider, models in SUPPORTED_MODELS.items():
        if model_name in models:
            return provider
    return "openai"  # Fallback provider

def get_llm(model_name: str = DEFAULT_MODEL, temperature: float = 0.7, api_key: str = None, streaming: bool = False, callbacks: list = None):
    """Factory to initialize LLM with the provided configurations.
    
    This factory automatically routes to the appropriate provider's LLM class.
    """
    provider = _get_provider(model_name)
    
    kwargs = {
        "model": model_name,
        "temperature": temperature,
        "streaming": streaming,
        "callbacks": callbacks or []
    }
    
    if provider == "google":
        if api_key:
            kwargs["google_api_key"] = api_key
        return ChatGoogleGenerativeAI(**kwargs)
    else:  # default to openai
        if api_key:
            kwargs["api_key"] = api_key
        return ChatOpenAI(**kwargs)
