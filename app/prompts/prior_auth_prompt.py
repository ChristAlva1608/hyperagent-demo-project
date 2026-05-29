from langchain_core.prompts import ChatPromptTemplate

# PRIOR_AUTH_PROMPT defined with {format_instructions} and the dynamic variable under section "## Patient Note"
PRIOR_AUTH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a professional medical assistant specialized in clinical data extraction and prior authorization processing.
Your task is to extract information from the patient note to populate the prior authorization form fields.

Strictly adhere to the following output format. If a value is missing or cannot be inferred, set it to null. Do not make up information.

{format_instructions}"""),
    ("human", """## Patient Note
{patient_note}""")
])