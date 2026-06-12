# backend/app/api/routes/user.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.saved import SavedQuery, SavedSection
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

async def get_current_user_id(
    firebase_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    email = firebase_user.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Firebase token missing email")
    
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Auto-create user if they login via Firebase but don't exist yet
        user = User(
            email=email,
            supabase_id=firebase_user.get("uid"),
            full_name=firebase_user.get("name"),
            is_lawyer=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user.id

@router.get("/saved-queries")
async def get_saved_queries(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    stmt = select(SavedQuery).where(SavedQuery.user_id == user_id).order_by(SavedQuery.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/saved-queries")
async def save_query(query: str, answer: str, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    db_item = SavedQuery(user_id=user_id, query_text=query, answer_text=answer)
    db.add(db_item)
    await db.commit()
    return {"status": "saved"}

@router.get("/saved-sections")
async def get_saved_sections(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    stmt = select(SavedSection).where(SavedSection.user_id == user_id).order_by(SavedSection.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/saved-sections")
async def save_section(section_id: int, act_title: str, section_number: str, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    db_item = SavedSection(user_id=user_id, section_id=section_id, act_title=act_title, section_number=section_number)
    db.add(db_item)
    await db.commit()
    return {"status": "saved"}

@router.delete("/saved-sections/{id}")
async def unsave_section(id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    stmt = delete(SavedSection).where(SavedSection.id == id, SavedSection.user_id == user_id)
    await db.execute(stmt)
    await db.commit()
    return {"status": "deleted"}

@router.delete("/saved-queries/{id}")
async def unsave_query(id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    stmt = delete(SavedQuery).where(SavedQuery.id == id, SavedQuery.user_id == user_id)
    await db.execute(stmt)
    await db.commit()
    return {"status": "deleted"}
