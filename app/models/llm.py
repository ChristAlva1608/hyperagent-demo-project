from langchain_openai import ChatOpenAI
from config import DEFAULT_MODEL

def get_llm(model_name: str = DEFAULT_MODEL, temperature: float = 0.7, api_key: str = None, streaming: bool = False, callbacks: list = None):
    """Factory to initialize LLM with the provided configurations."""
    kwargs = {
        "model": model_name,
        "temperature": temperature,
        "streaming": streaming,
        "callbacks": callbacks or []
    }
    
    if api_key:
        kwargs["api_key"] = api_key
        
    return ChatOpenAI(**kwargs)