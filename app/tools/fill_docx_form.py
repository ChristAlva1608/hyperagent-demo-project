import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

logger = logging.getLogger(__name__)

def fill_docx_form_tool(data: str) -> Tuple[bytes, str]:
    """
    Fill a DOCX prior authorization template with extracted clinical data and return file bytes.
    
    This tool takes the extracted clinical information (as JSON string) and populates a 
    prior authorization DOCX template, returning the file as bytes for download.
    
    Args:
        data: JSON string containing the extracted clinical fields from the patient note.
              This should be the output from generate_prior_auth tool.
    
    Returns:
        Tuple of (file_bytes, filename) for download, or raises an exception on error.
    
    Note:
        Currently uses a hardcoded template path: 'app/data/templates/prior_authorization_template.docx'
        Future enhancement: Allow users to upload custom templates or select from multiple options.
    """
    logger.info(f"fill_docx_form_tool invoked with data length: {len(data)}")
    
    try:
        # Parse the JSON data
        try:
            data_dict = json.loads(data)
            logger.info(f"Successfully parsed JSON data with {len(data_dict)} fields")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {str(e)}")
            raise ValueError(f"Invalid JSON data - {str(e)}")
        
        # Hardcoded template path (TODO: make this configurable in future)
        template_path = Path(__file__).parent.parent / "data" / "templates" / "prior_authorization_template.docx"
        logger.info(f"Using template: {template_path}")
        
        if not template_path.exists():
            logger.error(f"Template file not found: {template_path}")
            raise FileNotFoundError(f"Template file not found at {template_path}")
        
        # Generate unique filename with timestamp
        timestamp = int(time.time())
        final_filename = f"prior_authorization_{timestamp}.docx"
        
        # Use temporary directory for processing
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / final_filename
            
            # Import and call the fill_template_docx utility
            try:
                from app.utils.fill_template_docx import fill_template_docx
            except ImportError:
                from utils.fill_template_docx import fill_template_docx
            
            # Fill the template
            logger.info(f"Filling template with data (temp output: {output_path})")
            fill_template_docx(
                template_path=str(template_path),
                data=data_dict,
                output_path=str(output_path)
            )
            
            # Read the file into bytes
            file_bytes = BytesIO()
            with open(output_path, "rb") as f:
                file_bytes.write(f.read())
            file_bytes.seek(0)
            
            logger.info(f"Successfully filled DOCX template. Filename: {final_filename}")
            return file_bytes.getvalue(), final_filename
    
    except Exception as e:
        logger.error(f"Error filling DOCX form: {str(e)}", exc_info=True)
        raise
