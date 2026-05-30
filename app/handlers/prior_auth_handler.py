import io
import base64
import logging
from typing import Any, Dict, List, Optional
from langchain_core.output_parsers import PydanticOutputParser
from langfuse.langchain import CallbackHandler

try:
    from app.models.prior_auth_model import get_prior_auth_output_model
    from app.utils.processing_file import processing_file
    from app.prompts.prior_auth_prompt import PRIOR_AUTH_PROMPT
    from app.models.llm import get_llm
    from app.utils.api_key_validator import get_provider_api_key
except ImportError:
    from models.prior_auth_model import get_prior_auth_output_model
    from utils.processing_file import processing_file
    from prompts.prior_auth_prompt import PRIOR_AUTH_PROMPT
    from models.llm import get_llm
    from utils.api_key_validator import get_provider_api_key

logger = logging.getLogger(__name__)

def prior_auth_handler(
    uploaded_file: Any,
    fields: List[Dict[str, Any]],
    content: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    provider: Optional[str] = None,
) -> Any:
    """
    Processes an uploaded patient note and/or content string and generates all information fields
    for a prior authorization form using PydanticOutputParser.

    Args:
        uploaded_file: The uploaded patient note file (.docx or .pdf) or None.
        fields: A list of dicts specifying fields to extract. Each dict should have
                'name', 'type', and 'description'.
        content: Optional patient note text content.
        model_name: Model name to use (default: dynamic / session state).
        temperature: Temperature for LLM (default: dynamic / session state).
        provider: AI provider to use (default: dynamic / session state).

    Returns:
        An instance of the dynamically generated Pydantic model containing the extracted fields.
    """
    # Resolve provider, model_name, and temperature dynamically
    import streamlit as st
    from config import ACTIVE_PROVIDER, ACTIVE_MODEL, ACTIVE_TEMPERATURE

    if provider is None:
        try:
            session_provider = st.session_state.get("provider")
        except Exception:
            session_provider = None
        provider = session_provider or ACTIVE_PROVIDER or "OpenAI (ChatGPT)"

    if model_name is None:
        try:
            session_model = st.session_state.get("model_name")
        except Exception:
            session_model = None
        model_name = session_model or ACTIVE_MODEL or "gpt-4o-mini"

    if temperature is None:
        try:
            session_temp = st.session_state.get("temperature")
        except Exception:
            session_temp = None
        if session_temp is not None:
            temperature = session_temp
        else:
            temperature = ACTIVE_TEMPERATURE if ACTIVE_TEMPERATURE is not None else 0.0

    # 1. Process the input (supports uploaded file, raw content string, or both)
    if isinstance(uploaded_file, str):
        import os
        if not os.path.exists(uploaded_file):
            logger.info("File path '%s' not found. Attempting to resolve it in workspace.", uploaded_file)
            # Check if it exists in 'app' folder
            app_path = os.path.join("app", uploaded_file)
            if os.path.exists(app_path):
                uploaded_file = app_path
                logger.info("Resolved file path to: %s", uploaded_file)
            else:
                # Search recursively in the current directory for a matching docx/pdf file
                base_name = os.path.basename(uploaded_file).lower()
                found = False
                for root, _, files in os.walk("."):
                    for file in files:
                        if file.lower() == base_name or (file.lower().startswith("sample_patient_note") and file.lower().endswith(".docx")):
                            uploaded_file = os.path.join(root, file)
                            logger.info("Resolved file path by pattern matching to: %s", uploaded_file)
                            found = True
                            break
                    if found:
                        break

    logger.info("prior_auth_handler input: uploaded_file=%s, provider=%s, model=%s", uploaded_file, provider, model_name)
    if uploaded_file is None:
        if not content:
            logger.error("Neither uploaded_file nor content was provided to prior_auth_handler")
            raise ValueError("Either uploaded_file or content must be provided.")
        processed = {"type": "text", "content": content}
    else:
        logger.info("Processing uploaded file: %s", uploaded_file)
        processed = processing_file(uploaded_file)
        if content:
            if processed["type"] == "text":
                docx_text = processed.get("content", "")
                if docx_text:
                    processed["content"] = f"{content}\n{docx_text}"
                else:
                    processed["content"] = content
    logger.info("Input processed successfully. Content type: %s", processed['type'])

    # 2. Get the dynamically generated Pydantic model for output structure
    logger.info("Generating Pydantic output model for %d fields", len(fields))
    output_model = get_prior_auth_output_model(fields)

    # 3. Create the Pydantic parser
    parser = PydanticOutputParser(pydantic_object=output_model)

    # 4. Get format instructions
    format_instructions = parser.get_format_instructions()

    # 5. Extract system prompt template and format format_instructions into it
    system_prompt_template = PRIOR_AUTH_PROMPT.messages[0].prompt.template
    system_message_content = system_prompt_template.format(format_instructions=format_instructions)

    # 6. Format the human message depending on whether the input is text (docx) or images (pdf)
    if processed["type"] == "text":
        logger.info("Formatting messages for text-based notes (docx or raw text)")
        human_message_content = f"## Patient Note\n{processed['content']}"
        messages = [
            ("system", system_message_content),
            ("human", human_message_content)
        ]
    elif processed["type"] == "images":
        logger.info("Formatting messages for image/PDF-based notes (images)")
        if content:
            human_content = [{"type": "text", "text": f"## Patient Note\n{content}"}]
        else:
            human_content = [{"type": "text", "text": "## Patient Note"}]
        for img in processed["content"]:
            # Convert PIL Image to JPEG base64 string
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            human_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}
            })
        messages = [
            ("system", system_message_content),
            ("human", human_content)
        ]
    else:
        logger.error("Unknown processed content type: %s", processed['type'])
        raise ValueError(f"Unknown processed content type: {processed['type']}")

    # 7. Initialize LLM using get_llm with dynamic provider support
    provider_str: str = provider if provider is not None else "OpenAI (ChatGPT)"
    model_str: str = model_name if model_name is not None else "gpt-4o-mini"
    temp_float: float = temperature if temperature is not None else 0.0

    logger.info("Initializing LLM %s with provider %s", model_str, provider_str)
    api_key = get_provider_api_key(provider_str)
    llm = get_llm(
        model_name=model_str,
        temperature=temp_float,
        api_key=api_key
    )

    # 8. Create and run the chain: prompt -> llm -> parser
    logger.info("Invoking LLM chain to extract information")
    chain = llm | parser
    try:
        result = chain.invoke(
            messages,
            config={
                "callbacks": [CallbackHandler()],
                "run_name": "Prior Authorization Generation",
            }
        )
        logger.info("LLM chain invoked successfully and returned extracted fields")
        logger.info("Output of prior_auth_handler: %s", result)
        return result
    except Exception as e:
        logger.error("Failed during LLM chain execution: %s", str(e), exc_info=True)
        raise e
