import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from utils.api_key_validator import check_provider_api_key, get_provider_api_key
from chains.chat_chain import get_conversational_chain
from handlers.stream_handler import StreamlitLLMCallbackHandler
from utils.theme import inject_theme

def render_chat_page():
    """Renders the LangChain chat page."""
    inject_theme()
    
    # Render Custom Hospital Navbar Header
    st.markdown(
        """
        <div class="hospital-header">
            <div>
                <h1>💬 Clinical Assistant &amp; Guidelines Support</h1>
                <p>Stateful Conversational LLM Loop with EHR Context Memories</p>
            </div>
            <div class="header-badge">
                <span class="live-dot"></span>Memory Registry Active
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write("This workspace orchestrates deep clinical reasoning chains. Ask questions about guidelines, patient histories, or billing codes.")
    

    
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
            
    # API key validation check
    provider = st.session_state.get("provider", "OpenAI (ChatGPT)")
    has_api_key = check_provider_api_key(provider)
    
    # Document Upload (Compact widget directly above the chat input box)
    st.write("📎 **Upload File (optional):**")
    uploaded_file = st.file_uploader(
        "Upload clinical notes or guidelines (.docx, .pdf)",
        type=["docx", "pdf"],
        label_visibility="collapsed"
    )
    
    file_context = ""
    if uploaded_file is not None:
        try:
            # Process the file using the existing utility in app/utils/processing_file.py
            from utils.processing_file import processing_file
            processed_data = processing_file(uploaded_file)
            if processed_data["type"] == "text":
                file_context = processed_data["content"]
                st.success(f"Successfully loaded text from {uploaded_file.name}")
            elif processed_data["type"] == "images":
                st.info(f"Loaded {len(processed_data['content'])} pages/images from {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    # Chat Input
    if prompt := st.chat_input(placeholder="Ask me anything..."):
        # Format user message to include file context if present
        user_message_content = prompt
        if file_context:
            user_message_content = (
                f"--- START OF ATTACHED FILE ({uploaded_file.name}) ---\n"
                f"{file_context}\n"
                f"--- END OF ATTACHED FILE ---\n\n"
                f"User Prompt: {prompt}"
            )

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            if file_context:
                st.caption(f"📎 Attached: {uploaded_file.name}")
            
        # Display assistant response container
        with st.chat_message("assistant"):
            if not has_api_key:
                st.markdown(
                    f"""
                    <div class="status-card error">
                        <h4>⚠️ Credentials Missing</h4>
                        <p>Please provide an API Key for <strong>{provider}</strong> in the
                        <a href="/Settings" target="_self" style="color:var(--error-text);font-weight:700;text-decoration:underline;">Settings page</a>
                        to activate live reasoning chains.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.stop()
                
            # Create a placeholder for streaming
            placeholder = st.empty()
            
            # Setup callback handler for streaming
            stream_handler = StreamlitLLMCallbackHandler(placeholder)
            
            # Retrieve current state from session/sidebar
            model_name = st.session_state.get("model_name", "gpt-4o-mini")
            temperature = st.session_state.get("temperature", 0.7)
            api_key = get_provider_api_key(provider)
            
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
                    {"input": user_message_content, "history": history.messages}
                )
                
                # Check if a DOCX file was generated and stored in session state
                if "generated_docx_file" in st.session_state and st.session_state.generated_docx_file:
                    file_data = st.session_state.generated_docx_file
                    st.markdown("---")
                    st.download_button(
                        label="📥 Download Prior Authorization Form",
                        data=file_data["bytes"],
                        file_name=file_data["filename"],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True
                    )
                    # Clear the file from session state after showing download button
                    st.session_state.generated_docx_file = None
                
                # Save to history
                history.add_user_message(user_message_content)
                history.add_ai_message(response)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")
    render_chat_page()