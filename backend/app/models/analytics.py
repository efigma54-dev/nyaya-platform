from __future__ import annotations
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base

class QueryLog(Base):
    __tablename__ = "query_logs"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    provider: Mapped[str | None] = mapped_column(String(100))
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    lang: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
