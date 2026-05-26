from langchain_core.output_parsers import StrOutputParser
from app.models.llm import get_llm
from app.prompts.templates import get_chat_prompt

def get_conversational_chain(model_name: str = None, temperature: float = 0.7, api_key: str = None, streaming: bool = False, callbacks: list = None):
    """Factory to build a conversational LLM chain with prompt and optional callbacks."""
    prompt = get_chat_prompt()
    
    llm = get_llm(
        model_name=model_name,
        temperature=temperature,
        api_key=api_key,
        streaming=streaming,
        callbacks=callbacks
    )
    
    # LCEL (LangChain Expression Language) chain definition
    chain = prompt | llm | StrOutputParser()
    
    return chain