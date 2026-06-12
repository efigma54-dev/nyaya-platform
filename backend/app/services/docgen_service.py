import logging
from typing import Dict, Any, List
from app.services.ai_router import route_and_call
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DocInput(BaseModel):
    template_type: str # 'rti', 'consumer', 'notice'
    user_details: str
    recipient_details: str
    subject: str
    facts: str
    demands: str = ""

async def generate_legal_document(data: DocInput) -> str:
    """
    Generates a formal legal document based on template type.
    """
    templates = {
        "rti": "RTI (Right to Information) Application",
        "consumer": "Consumer Complaint (District Commission)",
        "notice": "Legal Notice for Recovery/Performance"
    }
    
    template_name = templates.get(data.template_type, "Legal Document")
    
    prompt = f"""
    You are a professional legal drafter in India. Draft a formal {template_name} based on the following details.
    
    User/Complainant Details: {data.user_details}
    Recipient/Opposite Party Details: {data.recipient_details}
    Subject: {data.subject}
    Facts of the Case: {data.facts}
    Specific Demands/Information Requested: {data.demands}
    
    GUIDELINES:
    1. Use the standard Indian legal format for {template_name}.
    2. Ensure a formal, professional tone.
    3. Include a clear disclaimer at the top and bottom: "DRAFT ONLY - NOT A LEGAL DOCUMENT. CONSULT A LAWYER BEFORE FILING."
    4. For RTI: Include placeholders for IPO (Indian Postal Order) details.
    5. For Consumer Complaint: Mention the Consumer Protection Act 2019.
    6. For Legal Notice: Include a specific time period (e.g., 15 days) for compliance.
    7. Use numbered paragraphs for facts.
    """
    
    messages = [{"role": "user", "content": prompt}]
    system = f"You are an expert in drafting {template_name}s. Write in English."
    
    try:
        response, _ = await route_and_call(
            query=f"{data.template_type} draft generation",
            messages=messages,
            system_prompt=system,
            retrieved_sections=[],
            stream=False
        )
        return response
    except Exception as e:
        logger.error(f"Document generation failed: {e}")
        return f"Failed to generate {template_name}. Please try again later."
