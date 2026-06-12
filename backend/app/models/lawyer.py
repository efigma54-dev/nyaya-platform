from __future__ import annotations
import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Lawyer(Base):
    __tablename__ = "lawyers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    specialization: Mapped[str] = mapped_column(String(200), nullable=False) # e.g. Criminal, Family, Civil
    location: Mapped[str] = mapped_column(String(200), nullable=False) # e.g. New Delhi, Mumbai
    experience_years: Mapped[int] = mapped_column(Integer)
    bio: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_image_url: Mapped[str | None] = mapped_column(String(500))
    rating: Mapped[float] = mapped_column(Integer, default=5)
    
    inquiries: Mapped[list["LawyerInquiry"]] = relationship("LawyerInquiry", back_populates="lawyer")

class LawyerInquiry(Base):
    __tablename__ = "lawyer_inquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lawyer_id: Mapped[int] = mapped_column(ForeignKey("lawyers.id"), nullable=False)
    user_name: Mapped[str] = mapped_column(String(200), nullable=False)
    user_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    query_summary: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, contacted, closed
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lawyer: Mapped["Lawyer"] = relationship("Lawyer", back_populates="inquiries")
