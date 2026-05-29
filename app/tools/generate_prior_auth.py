import json
import os
import logging
from pathlib import Path
from typing import Optional
try:
    from app.handlers.prior_auth_handler import prior_auth_handler
except ImportError:
    from handlers.prior_auth_handler import prior_auth_handler

logger = logging.getLogger(__name__)

def generate_prior_auth_tool(
    uploaded_file_path: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """
    Generate a Prior Authorization form from a patient note.
    
    Args:
        uploaded_file_path: Path to uploaded patient note (.docx or .pdf)
        content: Raw text content of patient note (alternative to file)
    
    Returns:
        Path to the generated authorization form or error message
    """
    logger.info(f"generate_prior_auth_tool invoked with uploaded_file_path={uploaded_file_path}, content_len={len(content) if content else 0}")
    try:
        # Load field definitions from JSON
        fields_path = Path(__file__).parent.parent / "data" / "templates" / "extracted_fields.json"
        logger.info(f"Loading field definitions from {fields_path}")
        with open(fields_path, 'r', encoding='utf-8') as f:
            fields = json.load(f)
        logger.info(f"Successfully loaded {len(fields)} field definitions")
        
        # Call the handler
        logger.info("Calling prior_auth_handler to extract clinical details and fill forms")
        result = prior_auth_handler(
            uploaded_file=uploaded_file_path,
            fields=fields,
            content=content
        )
        
        logger.info(f"prior_auth_handler completed successfully. Result: {result}")
        return f"Prior Authorization form generated successfully: {result}"
    
    except FileNotFoundError as e:
        logger.error(f"Field definitions file not found: {str(e)}", exc_info=True)
        return f"Error: Field definitions file not found - {str(e)}"
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in field definitions: {str(e)}", exc_info=True)
        return f"Error: Invalid JSON in field definitions - {str(e)}"
    except Exception as e:
        logger.error(f"Error during prior auth generation: {str(e)}", exc_info=True)
        return f"Error generating Prior Authorization form: {str(e)}"
