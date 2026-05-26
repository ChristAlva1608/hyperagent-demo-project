from langchain_core.callbacks import BaseCallbackHandler
import streamlit as st

class StreamlitLLMCallbackHandler(BaseCallbackHandler):
    """Callback handler to stream LLM generation directly into a Streamlit container."""
    
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Runs when a new token is generated."""
        self.text += token
        self.container.markdown(self.text + "▌")

    def on_llm_end(self, response, **kwargs) -> None:
        """Runs when LLM finishing generating."""
        self.container.markdown(self.text)