import logging
from typing import Dict, Any
from app.services.ai_router import route_and_call
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class FIRInput(BaseModel):
    complainant_name: str
    incident_date: str
    incident_place: str
    accused_details: str
    narrative: str
    sections_matched: str = ""

async def generate_fir_draft(data: FIRInput) -> str:
    """
    Generates a formal FIR draft using AI.
    """
    prompt = f"""
    You are an expert Indian legal assistant. Generate a formal FIR (First Information Report) draft based on the following details.
    
    Complainant: {data.complainant_name}
    Date of Incident: {data.incident_date}
    Place of Incident: {data.incident_place}
    Accused Details: {data.accused_details}
    Incident Narrative: {data.narrative}
    Relevant Sections: {data.sections_matched}
    
    GUIDELINES:
    1. Use a formal, professional tone suitable for a police complaint.
    2. Address it to "The Station House Officer (SHO)".
    3. Structure: Subject line, Complainant details, Chronological events, Specific allegations, Request for action.
    4. Include a clear disclaimer at the top and bottom: "DRAFT ONLY - NOT A LEGAL DOCUMENT. CONSULT A LAWYER BEFORE FILING."
    5. Mention both IPC and BNS 2023 equivalents if applicable.
    6. Ensure the narrative is structured clearly in numbered paragraphs.
    """
    
    messages = [{"role": "user", "content": prompt}]
    system = "You are a professional legal drafter specialized in Indian Criminal Law. Write in English."
    
    try:
        response, _ = await route_and_call(
            query="FIR draft generation",
            messages=messages,
            system_prompt=system,
            retrieved_sections=[], # Not needed for direct drafting
            stream=False
        )
        return response
    except Exception as e:
        logger.error(f"FIR generation failed: {e}")
        return "Failed to generate FIR draft. Please try again later."
