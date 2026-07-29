from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.core.database import get_db
from nyaya.core.security import create_access_token, hash_password, verify_password
from nyaya.db.models.schema import User, UserRole
from nyaya.schemas import TokenOut, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(u: User) -> UserOut:
    return UserOut.model_validate(
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": u.role.value if isinstance(u.role, UserRole) else u.role,
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    stmt = select(User).where(func.lower(User.email) == payload.email.lower())
    res = await db.execute(stmt)
    if res.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="EMAIL_ALREADY_REGISTERED")
    u = User(
        email=payload.email.lower(),
        name=payload.name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(u)
    await db.flush()
    return _user_out(u)


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenOut:
    stmt = select(User).where(
        func.lower(User.email) == payload.email.lower(),
        User.is_active.is_(True),
    )
    res = await db.execute(stmt)
    u = res.scalar_one_or_none()
    if u is None or not verify_password(payload.password, u.hashed_password):
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
    token = create_access_token(u.id, extra={"role": u.role.value if isinstance(u.role, UserRole) else u.role})
    return TokenOut(access_token=token, token_type="bearer", user=_user_out(u))
