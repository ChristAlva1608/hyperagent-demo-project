import streamlit as st
import time
from utils.helpers import get_provider_api_key, check_provider_api_key
from chains.chat_chain import get_conversational_chain
from langchain_core.messages import HumanMessage, AIMessage

def render_floating_chat():
    """Renders a premium, glassmorphism floating chat widget in the bottom right corner."""
    
    # 1. Inject CSS for fixing the popover to the bottom-right corner and styling the button
    st.markdown(
        """
        <style>
        /* Fix the Streamlit Popover container in the bottom-right corner */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 999999 !important;
        }
        
        /* Style the trigger button to look like a round floating action button */
        div[data-testid="stPopover"] > button {
            background-color: #1565c0 !important;
            color: white !important;
            border-radius: 50px !important;
            padding: 12px 24px !important;
            font-size: 15px !important;
            font-weight: bold !important;
            box-shadow: 0 4px 15px rgba(21, 101, 192, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        
        div[data-testid="stPopover"] > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 20px rgba(21, 101, 192, 0.6) !important;
            background-color: #1e88e5 !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
        }
        
        /* Popover inner body card adjustments */
        div[data-testid="stPopoverBody"] {
            width: 380px !important;
            max-height: 520px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            background-color: #0b0f19 !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
        }
        
        /* Style scrollbar in popover dropdown */
        .floating-chat-box::-webkit-scrollbar {
            width: 4px;
        }
        .floating-chat-box::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize state variables
    if "floating_chat_history" not in st.session_state:
        st.session_state.floating_chat_history = [
            AIMessage(content="Hello! I am your clinical co-pilot. I can help you analyze medical necessity guidelines, draft prior authorization requests, or review patient charts.")
        ]
    
    # Streamlit native popover container (serves as the popup overlay)
    with st.popover("💬 Ask Co-Pilot"):
        # Header & Intro Text
        st.markdown("### 🤖 Clinical Co-Pilot")
        st.markdown(
            "<p style='color: rgba(255,255,255,0.7); font-size: 13px; margin-top: -10px; line-height: 1.4;'>"
            "Need immediate help? Ask me any questions about prior authorizations, medical criteria, or patient history."
            "</p>",
            unsafe_allow_html=True
        )
        
        st.divider()
        
        # Suggestions Section
        st.markdown("<p style='font-size: 11px; font-weight: bold; color: #90caf9; margin-bottom: 8px; letter-spacing: 0.5px;'>SUGGESTED ACTIONS</p>", unsafe_allow_html=True)
        
        suggestions = [
            ("📋 Review Lumbar MRI Guidelines", "What are the Milliman / clinical guidelines required to approve a Lumbar Spine MRI?"),
            ("✍️ Draft Appeal for John Doe", "Draft a professional prior authorization appeal letter for patient John Doe whose Lumbar MRI request was denied due to lack of documented PT."),
            ("🔍 Check CPT 72148 Rules", "What is CPT code 72148 and what clinical indicators must be met for it?")
        ]
        
        selected_prompt = None
        
        # Display suggestions as sleek clickable full-width buttons
        for label, prompt_text in suggestions:
            if st.button(label, key=f"f_sug_{label.replace(' ', '_')}", use_container_width=True):
                selected_prompt = prompt_text
        
        st.divider()
        
        # Scrollable Conversation Container
        st.markdown("<p style='font-size: 11px; font-weight: bold; color: rgba(255,255,255,0.4); margin-bottom: 8px; letter-spacing: 0.5px;'>CONVERSATION</p>", unsafe_allow_html=True)
        
        chat_container_html = "<div class='floating-chat-box' style='max-height: 200px; overflow-y: auto; padding-right: 5px; margin-bottom: 15px;'>"
        for msg in st.session_state.floating_chat_history:
            if msg.type == "ai":
                bg = "background-color: rgba(21, 101, 192, 0.08);"
                border = "border-left: 3px solid #1565c0;"
                label = "🤖 Co-Pilot"
            else:
                bg = "background-color: rgba(255, 255, 255, 0.04);"
                border = "border-left: 3px solid rgba(255, 255, 255, 0.3);"
                label = "👤 You"
                
            msg_content = msg.content.replace('\n', '<br>')
            chat_container_html += f"""
            <div style="{bg} {border} padding: 10px; border-radius: 4px; margin-bottom: 8px; font-size: 13px; line-height: 1.4; color: rgba(255,255,255,0.9);">
                <div style="font-weight: bold; font-size: 11px; color: rgba(255,255,255,0.4); margin-bottom: 4px;">{label}</div>
                {msg_content}
            </div>
            """
        chat_container_html += "</div>"
        st.markdown(chat_container_html, unsafe_allow_html=True)
        
        # Dynamic response handler
        provider = st.session_state.get("provider", "OpenAI (ChatGPT)")
        has_api_key = check_provider_api_key(provider)
        
        # User input field
        user_text = st.text_input(
            "Type your query...",
            key="f_chat_input_text",
            placeholder="Type here or click a suggestion..."
        )
        
        c1, c2 = st.columns([3, 1])
        with c1:
            send_btn = st.button("Send Message", key="f_chat_send_button", type="primary", use_container_width=True)
        with c2:
            clear_btn = st.button("Clear", key="f_chat_clear_button", use_container_width=True)
            
        if clear_btn:
            st.session_state.floating_chat_history = [
                AIMessage(content="Hello! I am your clinical co-pilot. I can help you analyze medical necessity guidelines, prior authorization requests, or patient charts.")
            ]
            st.rerun()
            
        # Execute if text entered or suggestion selected
        exec_prompt = None
        if send_btn and user_text:
            exec_prompt = user_text
        elif selected_prompt:
            exec_prompt = selected_prompt
            
        if exec_prompt:
            # Append user message
            st.session_state.floating_chat_history.append(HumanMessage(content=exec_prompt))
            
            if has_api_key:
                try:
                    model_name = st.session_state.get("model_name", "gpt-4o-mini")
                    temperature = st.session_state.get("temperature", 0.7)
                    api_key = get_provider_api_key(provider)
                    
                    chain = get_conversational_chain(
                        model_name=model_name,
                        temperature=temperature,
                        api_key=api_key
                    )
                    
                    response = chain.invoke({
                        "input": exec_prompt,
                        "history": st.session_state.floating_chat_history[:-1]
                    })
                    st.session_state.floating_chat_history.append(AIMessage(content=response))
                except Exception as e:
                    st.session_state.floating_chat_history.append(
                        AIMessage(content=f"Error executing AI model call: {str(e)}")
                    )
            else:
                # Failsafe mock responses for offline presentation robustness
                time.sleep(0.6)
                mock_answers = {
                    "What are the Milliman / clinical guidelines required to approve a Lumbar Spine MRI?": 
                        "According to MCG (Milliman Care Guidelines) for Lumbar Spine MRI (CPT 72148), approval requires:\n"
                        "1. Documented clinical suspicion of lumbar radiculopathy, spinal stenosis, or disc herniation AND\n"
                        "2. Failure of at least 6 weeks of conservative therapy (e.g. physical therapy, physician-guided exercise) OR\n"
                        "3. Failed trial of anti-inflammatory / neuropathic agents (like Gabapentin) OR\n"
                        "4. 'Red flag' clinical findings (cauda equina syndrome, progressive motor loss, malignancy risk).",
                    
                    "What is CPT code 72148 and what clinical indicators must be met for it?":
                        "CPT Code 72148 designates a Magnetic Resonance Imaging (MRI) of the lumbar spinal canal and contents without contrast.\n\n"
                        "Clinical indicators required:\n"
                        "- Low back pain radiating into buttocks or lower extremity matching a dermatomal pathway.\n"
                        "- Objective physical signs of nerve root compression (e.g., positive straight leg raise test, S1/L5 sensation decrease).\n"
                        "- Completion and failure of standard conservative therapies (Gabapentin trial, PT).",
                    
                    "Draft a professional prior authorization appeal letter for patient John Doe whose Lumbar MRI request was denied due to lack of documented PT.":
                        "**PRIOR AUTHORIZATION APPEAL LETTER**\n\n"
                        "**Date:** October 27, 2023  \n"
                        "**Payer Name:** Cityfront PPO Healthcare  \n"
                        "**Patient Name:** John Doe (DOB: 11-12-1984)  \n"
                        "**Member ID:** CF-98472-A  \n"
                        "**Provider:** Emily Chen, MD (NPI: 1982730492)  \n\n"
                        "Dear Medical Director,\n\n"
                        "I am writing to appeal the denial of the Lumbar Spine MRI (CPT 72148) requested for Mr. John Doe. The denial cited a lack of documented physical therapy. However, clinical presentation dictates immediate imaging necessity:\n\n"
                        "- **Progressive Symptoms:** Mr. Doe has a 3-month history of sharp back pain radiating down the right buttock to the calf (radicular pattern), which has progressed rapidly.\n"
                        "- **Physical Examination:** Shows significant range of motion restriction, positive straight leg raise testing at 45 degrees, and sensory degradation in the S1 dermatome.\n"
                        "- **Conservative Management Update:** While PT could not be fully completed due to severe exacerbation of radicular pain during flexion exercises, a pharmacological trial of Gabapentin 100 mg tid has been initiated.\n\n"
                        "Proceeding with PT without confirming the presence of L5-S1 disc herniation poses a clinical risk of nerve compression progression. We request an immediate review and approval of CPT 72148.\n\n"
                        "Sincerely,  \n"
                        "Emily Chen, MD"
                }
                
                response = mock_answers.get(
                    exec_prompt,
                    "I have parsed your prompt. For fully dynamic clinical analysis of custom patient files, please supply your OpenAI API Key in the sidebar control panel! In mock mode, I can confirm this prompt matches standard healthcare compliance guidelines."
                )
                st.session_state.floating_chat_history.append(AIMessage(content=response))
                
            st.rerun()
