import os
import io
import docx2txt
import logging
from pypdf import PdfReader
from pdf2image import convert_from_bytes
from PIL import Image

logger = logging.getLogger(__name__)

def ocr_image_to_text(img: Image.Image) -> str:
    """
    Helper function to run high-fidelity LLM vision-based OCR on a PIL Image.
    Fails gracefully if API keys or vision capabilities are missing.
    """
    import streamlit as st
    import base64
    from models.llm import get_llm
    from utils.api_key_validator import get_provider_api_key, check_provider_api_key
    from langchain_core.messages import HumanMessage

    provider = st.session_state.get("provider", "OpenAI (ChatGPT)")
    has_api_key = check_provider_api_key(provider)
    
    if not has_api_key:
        logger.warning("No API key available for LLM vision OCR. Returning fallback error tag.")
        return "[Error: API key is required to perform OCR text extraction on image documents]"
        
    model_name = st.session_state.get("model_name", "gpt-4o-mini")
    api_key = get_provider_api_key(provider)
    
    # Fallback to a vision model if DeepSeek is selected (which doesn't support direct vision calls in standard API)
    if "deepseek" in model_name.lower():
        logger.info("DeepSeek selected; falling back to gpt-4o-mini for OCR vision processing")
        model_name = "gpt-4o-mini"
        provider = "OpenAI (ChatGPT)"
        api_key = get_provider_api_key(provider)
        if not api_key:
            return "[Error: OpenAI API key is required as a fallback to perform OCR vision analysis on this document image]"

    try:
        # Buffer PIL Image to JPEG bytes
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        logger.info(f"Invoking LLM vision OCR ({model_name}) on image document")
        llm = get_llm(model_name=model_name, temperature=0.0, api_key=api_key)
        
        prompt_content = [
            {
                "type": "text",
                "text": (
                    "Extract all text, clinical details, symptoms, patient information, diagnoses, "
                    "ICD codes, current status, failed conservative therapies, and physician comments "
                    "verbatim from this clinical note image. Format your output strictly in clean Markdown."
                )
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
            }
        ]
        
        response = llm.invoke([HumanMessage(content=prompt_content)]).content
        return response
        
    except Exception as e:
        logger.error(f"Error executing LLM vision OCR: {str(e)}", exc_info=True)
        return f"[Error performing LLM vision OCR: {str(e)}]"


def processing_file(uploaded_file) -> dict:
    """
    Unified Ingestion & Normalization pipeline.
    Parses PDF, DOCX, TXT, and clinical note images, converting them into 
    a standardized Markdown canonical format.
    
    Args:
        uploaded_file: A Streamlit UploadedFile, file-like object, or file path.
        
    Returns:
        dict: A dictionary containing:
              - 'type': 'text'
              - 'content': Normalized Markdown text string.
    """
    if isinstance(uploaded_file, str):
        filename = uploaded_file
        file_bytes = None
        # Read file bytes from path
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                file_bytes = f.read()
    else:
        filename = getattr(uploaded_file, "name", "")
        if hasattr(uploaded_file, "getvalue"):
            file_bytes = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            file_bytes = uploaded_file.read()
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
        else:
            file_bytes = None

    if not filename:
        raise ValueError("Invalid file. Filename could not be determined.")

    _, ext = os.path.splitext(filename.lower())
    logger.info(f"Unified preprocessor running on file: {filename} (extension: {ext})")
    
    if ext not in [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"]:
        raise ValueError(f"Unsupported file format '{ext}'. Only .pdf, .docx, .txt, .png, .jpg, .jpeg are supported.")

    if file_bytes is None:
        raise ValueError(f"Could not read content from file: {filename}")

    # 1. Plain Text Ingestion
    if ext == ".txt":
        text = file_bytes.decode("utf-8", errors="ignore")
        markdown_content = f"# Clinical Document: {filename}\n\n{text}"
        return {"type": "text", "content": markdown_content}

    # 2. Word DOCX Ingestion
    elif ext == ".docx":
        raw_text = docx2txt.process(io.BytesIO(file_bytes))
        markdown_content = f"# Clinical Document (Word): {filename}\n\n{raw_text}"
        return {"type": "text", "content": markdown_content}

    # 3. PDF Ingestion (Digital extract + scanned PIL image fallback)
    elif ext == ".pdf":
        # First, attempt fast digital text extraction
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            digital_text = ""
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    digital_text += f"## Page {idx+1}\n{page_text}\n\n"
            
            # If we found sufficient digital text, treat it as digital PDF
            if len(digital_text.strip()) > 120:
                logger.info(f"Digital text extracted from PDF: {filename} (length: {len(digital_text)})")
                markdown_content = f"# Clinical Document (PDF): {filename}\n\n{digital_text}"
                return {"type": "text", "content": markdown_content}
        except Exception as e:
            logger.warning(f"Digital PDF extraction failed: {str(e)}. Falling back to image OCR.")

        # Scanned PDF Fallback: Convert to images and run LLM multi-modal OCR
        logger.info(f"PDF '{filename}' appears to be scanned. Converting to images for OCR...")
        try:
            images = convert_from_bytes(file_bytes)
            ocr_pages = []
            for idx, img in enumerate(images):
                logger.info(f"Running LLM OCR on page {idx+1} of scanned PDF")
                page_text = ocr_image_to_text(img)
                ocr_pages.append(f"## Page {idx+1}\n\n{page_text}")
            
            markdown_content = f"# Clinical Document (Scanned PDF): {filename}\n\n" + "\n\n".join(ocr_pages)
            return {"type": "text", "content": markdown_content}
        except Exception as e:
            logger.error(f"Scanned PDF image conversion or OCR failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process scanned PDF document: {str(e)}")

    # 4. Patient Note Images Ingestion
    elif ext in [".png", ".jpg", ".jpeg"]:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            logger.info(f"Image Note Ingestion: running OCR on image '{filename}'")
            extracted_text = ocr_image_to_text(img)
            markdown_content = f"# Clinical Document (Image): {filename}\n\n{extracted_text}"
            return {"type": "text", "content": markdown_content}
        except Exception as e:
            logger.error(f"Image note OCR failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process clinical image note: {str(e)}")

    else:
        raise ValueError(f"Unsupported file format '{ext}'. Only .pdf, .docx, .txt, .png, .jpg, .jpeg are supported.")