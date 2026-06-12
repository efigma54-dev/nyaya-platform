from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.lawyer import Lawyer, LawyerInquiry
from pydantic import BaseModel

router = APIRouter()

class InquiryRequest(BaseModel):
    lawyer_id: int
    user_name: str
    user_phone: str
    query_summary: str

@router.get("/")
async def list_lawyers(
    specialization: str | None = None,
    location: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Lawyer).where(Lawyer.is_verified.is_(True))
    if specialization:
        stmt = stmt.where(Lawyer.specialization.ilike(f"%{specialization}%"))
    if location:
        stmt = stmt.where(Lawyer.location.ilike(f"%{location}%"))
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/inquiry")
async def create_inquiry(body: InquiryRequest, db: AsyncSession = Depends(get_db)):
    inquiry = LawyerInquiry(
        lawyer_id=body.lawyer_id,
        user_name=body.user_name,
        user_phone=body.user_phone,
        query_summary=body.query_summary
    )
    db.add(inquiry)
    await db.commit()
    return {"message": "Inquiry submitted successfully. The lawyer will contact you soon."}
