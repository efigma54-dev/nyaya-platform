# backend/app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_lawyer: bool

@router.get("/me", response_model=UserOut)
async def read_users_me(
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
        user = User(
            email=email,
            supabase_id=firebase_user.get("uid"),
            full_name=firebase_user.get("name"),
            is_lawyer=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user
