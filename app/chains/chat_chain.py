from langchain_core.output_parsers import StrOutputParser
from models.llm import get_llm
from prompts.templates import get_chat_prompt

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

    from tools.tool_registry import get_tool_registry

    registry = get_tool_registry()
    tool_ids = registry.list_tools()
    tools = registry.get_tools_by_ids(tool_ids)
    
    if tools:
        llm = llm.bind_tools(tools)
    
    # LCEL (LangChain Expression Language) chain definition
    chain = prompt | llm | StrOutputParser()
    
    return chain
