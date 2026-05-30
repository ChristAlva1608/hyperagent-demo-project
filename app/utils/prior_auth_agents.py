import logging
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from models.llm import get_llm
from utils.api_key_validator import get_provider_api_key

logger = logging.getLogger(__name__)

def classify_document(markdown_text: str, provider: str, model_name: str) -> Dict[str, str]:
    """
    Classification Agent: Analyzes the normalized Markdown document and
    categorizes it into standard healthcare record types.
    """
    logger.info("Running Document Classification Agent")
    api_key = get_provider_api_key(provider)
    llm = get_llm(model_name=model_name, temperature=0.0, api_key=api_key)

    system_prompt = (
        "You are an expert medical records classifier for health insurance payers. "
        "Analyze the clinical document provided and classify it into exactly one of "
        "the following standard clinical categories:\n"
        "- Clinical Note\n"
        "- Progress Note\n"
        "- Lab Report\n"
        "- Imaging Report\n"
        "- Referral\n"
        "- Insurance Document\n"
        "- Supporting Evidence\n\n"
        "Output your response strictly as a JSON object with two fields:\n"
        "1. 'category': The exact category name matching one of the bullet points above.\n"
        "2. 'justification': A brief (1-sentence) clinical reason for your classification."
    )

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"## Clinical Document (Markdown):\n{markdown_text}")
        ]
        
        # Configure JSON output if supported or parse response
        response = llm.invoke(messages).content
        
        # Clean JSON markdown blocks if returned
        clean_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        
        logger.info(f"Classification completed. Category: {data.get('category')}")
        return {
            "category": data.get("category", "Clinical Note"),
            "justification": data.get("justification", "Extracted note text.")
        }
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}", exc_info=True)
        return {
            "category": "Clinical Note",
            "justification": f"Failed to classify: {str(e)}"
        }


def extract_medical_info(markdown_text: str, fields: List[Dict[str, Any]], provider: str, model_name: str) -> Dict[str, Any]:
    """
    Extraction Agent: Leverages the dynamic prior_auth_handler Pydantic parser
    to extract structured information matching the target fields list.
    """
    logger.info(f"Running Medical Information Extraction Agent for {len(fields)} fields")
    try:
        from app.handlers.prior_auth_handler import prior_auth_handler
    except ImportError:
        from handlers.prior_auth_handler import prior_auth_handler
    
    # Reusing the existing high-fidelity prior_auth_handler
    result_model = prior_auth_handler(
        uploaded_file=None,
        fields=fields,
        content=markdown_text,
        model_name=model_name,
        provider=provider
    )
    
    # Return as standard Python dictionary
    return result_model.model_dump()


def generate_clinical_summary(extracted_data: Dict[str, Any], provider: str, model_name: str) -> str:
    """
    Clinical Summary Agent: Synthesizes extracted patient and clinical findings
    into a comprehensive clinical necessity background report.
    """
    logger.info("Running Clinical Summary Generation Agent")
    api_key = get_provider_api_key(provider)
    llm = get_llm(model_name=model_name, temperature=0.3, api_key=api_key)

    system_prompt = (
        "You are a clinical reviewer specializing in medical necessity justification. "
        "Using the structured patient prior authorization data provided, generate a "
        "high-fidelity Medical Clinical Summary. Write the summary in a professional, "
        "objective, and clinical tone.\n\n"
        "Ensure your output is formatted in clean Markdown using exactly these headers:\n"
        "### 🧑‍⚕️ Patient Overview\n"
        "Provide a summary of the patient's age, gender, insurance member ID, and general clinical profile.\n\n"
        "### 📋 Clinical Background\n"
        "List all primary and secondary diagnoses, relevant ICD-10 codes, and clinical timeline or history.\n\n"
        "### 🧠 Current Symptoms & Status\n"
        "Describe the patient's current symptoms, pain severity, functional limitations, and daily impact.\n\n"
        "### 💊 Failed Conservative Therapies\n"
        "List failed treatments (physical therapy, specific drugs, home exercises) including durations and clinical failure reasons.\n\n"
        "### 💉 Requested Service & CPT Codes\n"
        "Specify the requested medication or procedure (e.g. Lumbar Spine MRI) and CPT codes (e.g. 72148).\n\n"
        "### 🔍 Medical Necessity Justification\n"
        "Provide a solid, evidence-based argument explaining why the requested service is medically necessary based on conservative treatment failure, neurologic status, and MCG guidelines."
    )

    try:
        formatted_input = json.dumps(extracted_data, indent=2)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"## Extracted Patient JSON:\n{formatted_input}")
        ]
        
        summary = llm.invoke(messages).content
        logger.info("Clinical Summary generated successfully")
        return summary
    except Exception as e:
        logger.error(f"Clinical Summary generation failed: {str(e)}", exc_info=True)
        return f"### ⚠️ Summary Generation Error\n\nFailed to generate clinical summary: {str(e)}"


def select_template(payer: str) -> str:
    """
    Dynamically maps the extracted insurance payer name to a corresponding
    document template path in data/templates/.
    """
    import os
    payer_lower = str(payer).lower().strip()
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "templates")
    
    if "aetna" in payer_lower:
        tpl_name = "aetna_prior_authorization_template.docx"
    elif "cigna" in payer_lower:
        tpl_name = "cigna_prior_authorization_template.docx"
    else:
        tpl_name = "prior_authorization_template.docx"
        
    target_path = os.path.join(base_dir, tpl_name)
    logger.info(f"Dynamic Template Selector: mapped payer '{payer}' to template '{tpl_name}'")
    
    if os.path.exists(target_path):
        return target_path
    
    return os.path.join(base_dir, "prior_authorization_template.docx")
