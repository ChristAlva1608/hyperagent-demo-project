import json
import os
from pathlib import Path
from typing import Optional
try:
    from app.handlers.prior_auth_handler import prior_auth_handler
except ImportError:
    from handlers.prior_auth_handler import prior_auth_handler

def generate_prior_auth_tool(
    uploaded_file_path: Optional[str] = None,
    content: Optional[str] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Generate a Prior Authorization form from a patient note.
    
    Args:
        uploaded_file_path: Path to uploaded patient note (.docx or .pdf)
        content: Raw text content of patient note (alternative to file)
        api_key: Optional OpenAI API key
    
    Returns:
        Path to the generated authorization form or error message
    """
    try:
        # Load field definitions from JSON
        fields_path = Path(__file__).parent.parent / "data" / "templates" / "extracted_fields.json"
        with open(fields_path, 'r', encoding='utf-8') as f:
            fields = json.load(f)
        
        # Call the handler
        result = prior_auth_handler(
            uploaded_file=uploaded_file_path,
            fields=fields,
            api_key=api_key,
            content=content
        )
        
        return f"Prior Authorization form generated successfully: {result}"
    
    except FileNotFoundError as e:
        return f"Error: Field definitions file not found - {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in field definitions - {str(e)}"
    except Exception as e:
        return f"Error generating Prior Authorization form: {str(e)}"