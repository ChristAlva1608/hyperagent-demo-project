import io
import base64
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

from app.models.prior_auth_model import get_prior_auth_output_model
from app.utils.processing_file import processing_file
from app.prompts.prior_auth_prompt import PRIOR_AUTH_PROMPT


def prior_auth_handler(
    uploaded_file: Any,
    fields: List[Dict[str, Any]],
    api_key: str = None,
    content: str = None,
) -> Any:
    """
    Processes an uploaded patient note and/or content string and generates all information fields
    for a prior authorization form using PydanticOutputParser and gpt-4.1-mini.

    Args:
        uploaded_file: The uploaded patient note file (.docx or .pdf) or None.
        fields: A list of dicts specifying fields to extract. Each dict should have
                'name', 'type', and 'description'.
        api_key: Optional OpenAI API key.
        content: Optional patient note text content.

    Returns:
        An instance of the dynamically generated Pydantic model containing the extracted fields.
    """
    # 1. Process the input (supports uploaded file, raw content string, or both)
    if uploaded_file is None:
        if not content:
            raise ValueError("Either uploaded_file or content must be provided.")
        processed = {"type": "text", "content": content}
    else:
        processed = processing_file(uploaded_file)
        if content:
            if processed["type"] == "text":
                docx_text = processed.get("content", "")
                if docx_text:
                    processed["content"] = f"{content}\n{docx_text}"
                else:
                    processed["content"] = content

    # 2. Get the dynamically generated Pydantic model for output structure
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
        human_message_content = f"## Patient Note\n{processed['content']}"
        messages = [
            ("system", system_message_content),
            ("human", human_message_content)
        ]
    elif processed["type"] == "images":
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
        raise ValueError(f"Unknown processed content type: {processed['type']}")

    # 7. Initialize ChatOpenAI with gpt-4o-mini
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        openai_api_key=api_key
    )

    # 8. Create and run the chain: prompt -> llm -> parser
    chain = llm | parser
    result = chain.invoke(messages)

    return result