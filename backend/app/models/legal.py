
# backend/app/models/legal.py

import enum

from sqlalchemy import (
    ARRAY,
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
    RULE = "rule"
    NOTIFICATION = "notification"


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

    # Relationships
    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter", back_populates="act", cascade="all, delete-orphan"
    )
    sections: Mapped[list["Section"]] = relationship(
        "Section", back_populates="act", cascade="all, delete-orphan"
    )


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id"), nullable=False)
    chapter_number: Mapped[str] = mapped_column(String(50), nullable=False)
    chapter_title: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    act: Mapped["Act"] = relationship("Act", back_populates="chapters")
    sections: Mapped[list["Section"]] = relationship(
        "Section", back_populates="chapter", cascade="all, delete-orphan"
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id"), nullable=False)
    chapter_id: Mapped[int | None] = mapped_column(ForeignKey("chapters.id"))

    # Identity
    section_number: Mapped[str] = mapped_column(String(50), nullable=False)
    section_title: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int | None] = mapped_column(Integer)

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

    # Additional metadata
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    related_section_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    effective_date: Mapped[str | None] = mapped_column(String(50))

    # Vector search
    qdrant_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100))

    # Flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_amended: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    act: Mapped["Act"] = relationship("Act", back_populates="sections")
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="sections")
    subsections: Mapped[list["Subsection"]] = relationship(
        "Subsection", back_populates="section", cascade="all, delete-orphan"
    )
    explanations: Mapped[list["Explanation"]] = relationship(
        "Explanation", back_populates="section", cascade="all, delete-orphan"
    )
    illustrations: Mapped[list["Illustration"]] = relationship(
        "Illustration", back_populates="section", cascade="all, delete-orphan"
    )
    exceptions: Mapped[list["Exception"]] = relationship(
        "Exception", back_populates="section", cascade="all, delete-orphan"
    )
    provisos: Mapped[list["Proviso"]] = relationship(
        "Proviso", back_populates="section", cascade="all, delete-orphan"
    )
    amendments: Mapped[list["Amendment"]] = relationship(
        "Amendment", back_populates="section"
    )
    linked_judgments: Mapped[list["JudgmentSection"]] = relationship(
        "JudgmentSection", back_populates="section"
    )
    linked_rules: Mapped[list["RuleSection"]] = relationship(
        "RuleSection", back_populates="section"
    )

    __table_args__ = (Index("ix_sections_act_number", "act_id", "section_number"),)


class Subsection(Base):
    __tablename__ = "subsections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    subsection_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bare_text: Mapped[str] = mapped_column(Text, nullable=False)
    plain_language: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    section: Mapped["Section"] = relationship("Section", back_populates="subsections")


class Explanation(Base):
    __tablename__ = "explanations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    explanation_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bare_text: Mapped[str] = mapped_column(Text, nullable=False)
    plain_language: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    section: Mapped["Section"] = relationship("Section", back_populates="explanations")


class Illustration(Base):
    __tablename__ = "illustrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    illustration_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bare_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    section: Mapped["Section"] = relationship("Section", back_populates="illustrations")


class Exception(Base):
    __tablename__ = "exceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    exception_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bare_text: Mapped[str] = mapped_column(Text, nullable=False)
    plain_language: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    section: Mapped["Section"] = relationship("Section", back_populates="exceptions")


class Proviso(Base):
    __tablename__ = "provisos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    proviso_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bare_text: Mapped[str] = mapped_column(Text, nullable=False)
    plain_language: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    section: Mapped["Section"] = relationship("Section", back_populates="provisos")


class Judgment(Base):
    __tablename__ = "judgments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_title: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    bench: Mapped[str | None] = mapped_column(String(500))
    citation: Mapped[str | None] = mapped_column(String(500), nullable=False, index=True)
    court: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100))
    judgment_date: Mapped[str | None] = mapped_column(String(50))
    legal_principles: Mapped[Text | None] = mapped_column(Text)
    key_paragraphs: Mapped[Text | None] = mapped_column(Text)
    holdings: Mapped[Text | None] = mapped_column(Text)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    full_text_url: Mapped[str | None] = mapped_column(String(500))
    source: Mapped[str | None] = mapped_column(String(100))  # e.g., Indian Kanoon, SCC

    qdrant_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    linked_sections: Mapped[list["JudgmentSection"]] = relationship(
        "JudgmentSection", back_populates="judgment"
    )


class JudgmentSection(Base):
    __tablename__ = "judgment_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    judgment_id: Mapped[int] = mapped_column(ForeignKey("judgments.id"), nullable=False)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    judgment: Mapped["Judgment"] = relationship("Judgment", back_populates="linked_sections")
    section: Mapped["Section"] = relationship("Section", back_populates="linked_judgments")

    __table_args__ = (
        Index("ix_judgment_section", "judgment_id", "section_id", unique=True),
    )


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    full_title: Mapped[str] = mapped_column(String(500), nullable=False)
    act_id: Mapped[int | None] = mapped_column(ForeignKey("acts.id"))
    year: Mapped[int | None] = mapped_column(Integer)
    category: Mapped[LawCategory] = mapped_column(
        SAEnum(LawCategory), nullable=False
    )
    state: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(500))
    full_text: Mapped[Text | None] = mapped_column(Text)

    qdrant_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    linked_sections: Mapped[list["RuleSection"]] = relationship(
        "RuleSection", back_populates="rule"
    )


class RuleSection(Base):
    __tablename__ = "rule_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id"), nullable=False)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    rule: Mapped["Rule"] = relationship("Rule", back_populates="linked_sections")
    section: Mapped["Section"] = relationship("Section", back_populates="linked_rules")

    __table_args__ = (
        Index("ix_rule_section", "rule_id", "section_id", unique=True),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    full_title: Mapped[str] = mapped_column(String(500), nullable=False)
    issuing_authority: Mapped[str] = mapped_column(String(200), nullable=False)
    notification_date: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[LawCategory] = mapped_column(
        SAEnum(LawCategory), nullable=False
    )
    state: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(500))
    full_text: Mapped[Text | None] = mapped_column(Text)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    qdrant_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


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
