from fastapi import APIRouter, HTTPException
from app.services.docgen_service import DocInput, generate_legal_document
from app.services.fir_service import FIRInput, generate_fir_draft

router = APIRouter()

@router.post("/fir")
async def create_fir_draft_alias(body: FIRInput):
    """Alias for frontend POST /api/generate/fir → /generate/fir."""
    if not body.narrative or len(body.narrative) < 10:
        raise HTTPException(400, "Narrative too short")
    draft = await generate_fir_draft(body)
    return {"draft": draft}


@router.post("/generate")
async def create_document(body: DocInput):
    """
    Endpoint to generate various legal documents.
    """
    if not body.facts or len(body.facts) < 10:
        raise HTTPException(400, "Facts section too short")
    
    draft = await generate_legal_document(body)
    return {"draft": draft}

@router.get("/templates")
async def get_templates():
    """
    Returns list of available document templates.
    """
    return [
        {"id": "fir", "title": "FIR Draft", "desc": "Police complaint for criminal incidents"},
        {"id": "rti", "title": "RTI Application", "desc": "Request info from government bodies"},
        {"id": "consumer", "title": "Consumer Complaint", "desc": "For defective goods or bad service"},
        {"id": "notice", "title": "Legal Notice", "desc": "Demand letter for money or performance"}
    ]
