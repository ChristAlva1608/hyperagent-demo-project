from langchain_core.prompts import ChatPromptTemplate

# Example fields configuration for prior authorization
FILLABLE_FIELDS = [
    {
        "name": "request_type",
        "type": "str",
        "description": "Type of authorization request. Example: 'standard', 'quick_response', or 'expedited'. Set null if no information."
    },
    {
        "name": "pre_scheduled_date_of_service",
        "type": "str",
        "description": "Scheduled date for the requested medical service. Format YYYY-MM-DD. Set null if no information."
    },
    {
        "name": "authorization_needed_by_date",
        "type": "str",
        "description": "Date by which authorization approval is needed. Format YYYY-MM-DD. Set null if no information."
    },
    {
        "name": "expedited_request_physician_signature",
        "type": "str",
        "description": "Physician signature approving expedited request processing. Set null if no information."
    },

    # Member Information
    {
        "name": "member_last_name",
        "type": "str",
        "description": "Last name of the patient/member. Set null if no information."
    },
    {
        "name": "member_first_name",
        "type": "str",
        "description": "First name of the patient/member. Set null if no information."
    },
    {
        "name": "member_id",
        "type": "str",
        "description": "Insurance member ID or subscriber ID. Set null if no information."
    },
    {
        "name": "date_of_birth",
        "type": "str",
        "description": "Date of birth of the patient. Format YYYY-MM-DD. Set null if no information."
    },
    {
        "name": "gender",
        "type": "str",
        "description": "Gender of the patient. Example: 'M' or 'F'. Set null if no information."
    },

    # Requesting Provider Information
    {
        "name": "requesting_provider_name",
        "type": "str",
        "description": "Name of the requesting provider, primary care physician, or specialist. Set null if no information."
    },
    {
        "name": "requesting_provider_number_or_tax_id",
        "type": "str",
        "description": "Provider number or tax ID of the requesting provider. Set null if no information."
    },
    {
        "name": "requesting_provider_npi",
        "type": "str",
        "description": "National Provider Identifier (NPI) of the requesting provider. Set null if no information."
    },
    {
        "name": "requesting_provider_phone",
        "type": "str",
        "description": "Telephone number of the requesting provider. Set null if no information."
    },
    {
        "name": "requesting_provider_fax",
        "type": "str",
        "description": "Fax number of the requesting provider. Set null if no information."
    },
    {
        "name": "requesting_provider_contact_person",
        "type": "str",
        "description": "Contact person for the requesting provider office. Set null if no information."
    },

    # Service Provider / Facility
    {
        "name": "service_provider_name",
        "type": "str",
        "description": "Name of the service provider or facility such as hospital, surgery center, or DME provider. Set null if no information."
    },
    {
        "name": "service_provider_address",
        "type": "str",
        "description": "Address of the service provider or facility. Set null if no information."
    },
    {
        "name": "service_provider_tax_id",
        "type": "str",
        "description": "Tax ID of the service provider or facility. Set null if no information."
    },
    {
        "name": "service_provider_npi",
        "type": "str",
        "description": "National Provider Identifier (NPI) of the service provider or facility. Set null if no information."
    },
    {
        "name": "service_provider_phone",
        "type": "str",
        "description": "Telephone number of the service provider or facility. Set null if no information."
    },
    {
        "name": "service_provider_fax",
        "type": "str",
        "description": "Fax number of the service provider or facility. Set null if no information."
    },
    {
        "name": "service_provider_contact_person",
        "type": "str",
        "description": "Contact person for the service provider or facility. Set null if no information."
    },

    # Requested Service Categories
    {
        "name": "requested_service_types",
        "type": "list[str]",
        "description": "List of requested service categories selected in the form. Examples: ['out_patient_surgery', 'pain_management']. Set empty list if no information."
    },

    # Clinical Trial
    {
        "name": "clinical_trial_type",
        "type": "str",
        "description": "Clinical trial insurance type if applicable. Example: 'commercial' or 'medicare'. Set null if no information."
    },

    # Diagnosis Information
    {
        "name": "diagnosis_codes",
        "type": "list[str]",
        "description": "List of ICD diagnosis codes related to the request. Set empty list if no information."
    },
    {
        "name": "diagnosis_descriptions",
        "type": "list[str]",
        "description": "List of diagnosis descriptions corresponding to ICD codes. Set empty list if no information."
    },

    # Procedure Information
    {
        "name": "procedure_codes",
        "type": "list[str]",
        "description": "List of CPT or HCPCS procedure codes requested for authorization. Set empty list if no information."
    },
    {
        "name": "procedure_descriptions",
        "type": "list[str]",
        "description": "List of descriptions corresponding to CPT or HCPCS procedure codes. Set empty list if no information."
    },

    # Supporting Clinical Information
    {
        "name": "supporting_chart_notes_available",
        "type": "bool",
        "description": "Whether supporting chart notes are attached or available. Set null if no information."
    },
    {
        "name": "diagnostic_tests_summary",
        "type": "str",
        "description": "Summary of diagnostic tests such as MRI, CT, X-ray, or laboratory results supporting medical necessity. Set null if no information."
    },
    {
        "name": "lab_values_summary",
        "type": "str",
        "description": "Relevant laboratory values supporting the authorization request. Set null if no information."
    },
    {
        "name": "medical_necessity_statement",
        "type": "str",
        "description": "Clinical justification explaining why the requested treatment or procedure is medically necessary. Set null if no information."
    },
    {
        "name": "failed_conservative_treatments",
        "type": "list[str]",
        "description": "List of prior failed conservative treatments such as medications, physical therapy, injections, or home exercise programs. Set empty list if no information."
    },
    {
        "name": "functional_impairment_description",
        "type": "str",
        "description": "Description of how the condition affects the patient's daily functioning or quality of life. Set null if no information."
    },

    # Additional Notes
    {
        "name": "authorization_change_notes",
        "type": "str",
        "description": "Additional information or requested changes related to an existing authorization. Set null if no information."
    }
]

# PRIOR_AUTH_PROMPT defined with {format_instructions} and the dynamic variable under section "## Patient Note"
PRIOR_AUTH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a professional medical assistant specialized in clinical data extraction and prior authorization processing.
Your task is to extract information from the patient note to populate the prior authorization form fields.

Strictly adhere to the following output format. If a value is missing or cannot be inferred, set it to null. Do not make up information.

{format_instructions}"""),
    ("human", """## Patient Note
{patient_note}""")
])