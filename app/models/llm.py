from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config import DEFAULT_MODEL
import os

def get_llm(model_name: str = DEFAULT_MODEL, temperature: float = 0.7, api_key: str = None, streaming: bool = False, callbacks: list = None):
    """Factory to initialize the appropriate LLM class based on the model name."""
    m_lower = model_name.lower()
    
    # 1. Google Gemini Provider
    if "gemini" in m_lower:
        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "callbacks": callbacks or []
        }
        # Locate API Key
        actual_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if actual_key:
            kwargs["google_api_key"] = actual_key
        return ChatGoogleGenerativeAI(**kwargs)
        
    # 2. DeepSeek Provider (API is 100% OpenAI compatible)
    elif "deepseek" in m_lower:
        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "streaming": streaming,
            "callbacks": callbacks or [],
            "openai_api_base": "https://api.deepseek.com/v1"
        }
        # Locate API Key
        actual_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if actual_key:
            kwargs["api_key"] = actual_key
        return ChatOpenAI(**kwargs)
        
    # 3. Default: OpenAI Provider (ChatGPT)
    else:
        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "streaming": streaming,
            "callbacks": callbacks or []
        }
        # Locate API Key
        actual_key = api_key or os.getenv("OPENAI_API_KEY")
        if actual_key:
            kwargs["api_key"] = actual_key
        return ChatOpenAI(**kwargs)