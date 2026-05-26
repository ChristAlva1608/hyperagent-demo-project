import os
import io
import docx2txt
from pdf2image import convert_from_bytes, convert_from_path

def processing_file(uploaded_file):
    """
    Process an uploaded file.
    Only supports .docx and .pdf files.
    
    Args:
        uploaded_file: A Streamlit UploadedFile, file-like object, or file path.
        
    Returns:
        dict: A dictionary containing the type ('text' or 'images') and the content.
        
    Raises:
        ValueError: If the file extension is not supported.
    """
    if isinstance(uploaded_file, str):
        filename = uploaded_file
        file_bytes = None
    else:
        filename = getattr(uploaded_file, "name", "")
        if hasattr(uploaded_file, "getvalue"):
            file_bytes = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            # Ensure we start from the beginning
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

    if ext == ".docx":
        if file_bytes is not None:
            text = docx2txt.process(io.BytesIO(file_bytes))
        else:
            text = docx2txt.process(filename)
        return {"type": "text", "content": text}
        
    elif ext == ".pdf":
        if file_bytes is not None:
            images = convert_from_bytes(file_bytes)
        else:
            images = convert_from_path(filename)
        return {"type": "images", "content": images}
        
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Only .docx and .pdf are supported.")