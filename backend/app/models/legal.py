# backend/app/models/legal.py

import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ActType(str, enum.Enum):
    CENTRAL = "central"
    STATE = "state"
    CONSTITUTIONAL = "constitutional"
    REGULATION = "regulation"


class LawCategory(str, enum.Enum):
    CRIMINAL = "criminal"
    CIVIL = "civil"
    FAMILY = "family"
    PROPERTY = "property"
    LABOUR = "labour"
    CONSTITUTIONAL = "constitutional"
    CORPORATE = "corporate"
    CONSUMER = "consumer"
    CYBER = "cyber"
    ENVIRONMENTAL = "environmental"
    TAX = "tax"
    IPR = "ipr"
    NARCOTICS = "narcotics"
    OTHER = "other"


class Act(Base):
    __tablename__ = "acts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    full_title: Mapped[str] = mapped_column(String(500), nullable=False)
    act_number: Mapped[str | None] = mapped_column(String(50))
    year: Mapped[int | None] = mapped_column(Integer)
    act_type: Mapped[ActType] = mapped_column(
        SAEnum(ActType), default=ActType.CENTRAL, nullable=False
    )
    category: Mapped[LawCategory] = mapped_column(
        SAEnum(LawCategory), nullable=False
    )
    state: Mapped[str | None] = mapped_column(String(100))  # null = central
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    replaces_act_id: Mapped[int | None] = mapped_column(ForeignKey("acts.id"))
    source_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sections: Mapped[list["Section"]] = relationship(
        "Section", back_populates="act", cascade="all, delete-orphan"
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id"), nullable=False)

    # Identity
    section_number: Mapped[str] = mapped_column(String(50), nullable=False)
    section_title: Mapped[str | None] = mapped_column(String(500))

    # Content — two versions, both required
    bare_text: Mapped[str] = mapped_column(Text, nullable=False)
    plain_language: Mapped[str | None] = mapped_column(Text)

    # Criminal metadata
    is_bailable: Mapped[bool | None] = mapped_column(Boolean)
    is_cognizable: Mapped[bool | None] = mapped_column(Boolean)
    is_compoundable: Mapped[bool | None] = mapped_column(Boolean)
    punishment_summary: Mapped[str | None] = mapped_column(String(500))
    min_punishment: Mapped[str | None] = mapped_column(String(200))
    max_punishment: Mapped[str | None] = mapped_column(String(200))
    fine_amount: Mapped[str | None] = mapped_column(String(200))
    relevant_court: Mapped[str | None] = mapped_column(String(200))
    limitation_period: Mapped[str | None] = mapped_column(String(200))

    # Vector search
    qdrant_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100))

    # Flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_amended: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    act: Mapped["Act"] = relationship("Act", back_populates="sections")
    amendments: Mapped[list["Amendment"]] = relationship(
        "Amendment", back_populates="section"
    )

    __table_args__ = (Index("ix_sections_act_number", "act_id", "section_number"),)


class Amendment(Base):
    __tablename__ = "amendments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    effective_date: Mapped[str | None] = mapped_column(String(50))
    old_text: Mapped[str | None] = mapped_column(Text)
    new_text: Mapped[str] = mapped_column(Text, nullable=False)
    amendment_act: Mapped[str | None] = mapped_column(String(300))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    section: Mapped["Section"] = relationship("Section", back_populates="amendments")
