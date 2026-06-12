from fastapi import APIRouter, HTTPException
from app.services.fir_service import FIRInput, generate_fir_draft

router = APIRouter()

@router.post("/generate")
async def create_fir_draft(body: FIRInput):
    """
    Endpoint to generate an FIR draft.
    """
    if not body.narrative or len(body.narrative) < 10:
        raise HTTPException(400, "Narrative too short")
    
    draft = await generate_fir_draft(body)
    return {"draft": draft}
