import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from components.sidebar import render_sidebar
from utils.helpers import check_api_key, get_api_key, get_provider
from chains.chat_chain import get_conversational_chain
from handlers.stream_handler import StreamlitLLMCallbackHandler

def render_chat_page():
    """Renders the LangChain chat page."""
    st.title("💬 Chat Assistant")
    st.write("This page demonstrates integration with LangChain, including models, prompts, handlers, and memory.")
    
    # Render Sidebar Settings
    render_sidebar()
    
    # Initialize message history using Streamlit-native memory
    history = StreamlitChatMessageHistory(key="chat_messages")
    
    # Seed message if history is empty
    if len(history.messages) == 0:
        history.add_ai_message("How can I help you today?")
        
    # Render conversation history
    for msg in history.messages:
        role = "assistant" if msg.type == "ai" else "user"
        with st.chat_message(role):
            st.write(msg.content)
            
    # Retrieve current state from session/sidebar
    model_name = st.session_state.get("model_name", "gpt-4o-mini")
    temperature = st.session_state.get("temperature", 0.7)
    
    # API key validation check
    has_api_key = check_api_key(model_name)
    
    # Chat Input
    if prompt := st.chat_input(placeholder="Ask me anything..."):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            
        # Display assistant response container
        with st.chat_message("assistant"):
            if not has_api_key:
                provider_display = "Google" if get_provider(model_name) == "google" else "OpenAI"
                st.error(f"Please provide a {provider_display} API Key in the sidebar or setup your .env file to run this model.")
                st.stop()
                
            # Create a placeholder for streaming
            placeholder = st.empty()
            
            # Setup callback handler for streaming
            stream_handler = StreamlitLLMCallbackHandler(placeholder)
            
            api_key = get_api_key(model_name)
            
            try:
                # Initialize Chain
                chain = get_conversational_chain(
                    model_name=model_name,
                    temperature=temperature,
                    api_key=api_key,
                    streaming=True,
                    callbacks=[stream_handler]
                )
                
                # Invoke chain with input and history list
                # StreamlitChatMessageHistory can be formatted to fit system/history templates
                response = chain.invoke(
                    {"input": prompt, "history": history.messages}
                )
                
                # Save to history
                history.add_user_message(prompt)
                history.add_ai_message(response)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")
    render_chat_page()