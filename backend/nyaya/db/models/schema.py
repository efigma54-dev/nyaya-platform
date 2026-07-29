from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nyaya.core.database import Base


class ActJurisdiction(str, enum.Enum):
    INDIA_CENTRAL = "india_central"
    INDIA_STATE = "india_state"


class ActStatus(str, enum.Enum):
    IN_FORCE = "in_force"
    REPEALED = "repealed"
    PARTIALLY_REPEALED = "partially_repealed"
    SUPERSEDED = "superseded"


class KGRelationType(str, enum.Enum):
    REPLACES = "replaces"
    REPLACED_BY = "replaced_by"
    AMENDED_BY = "amended_by"
    INTERPRETED_BY = "interpreted_by"
    CITED_IN = "cited_in"
    RELATED_SECTION = "related_section"
    ANALOGOUS_TO = "analogous_to"


class UserRole(str, enum.Enum):
    ANONYMOUS = "anonymous"
    RESEARCHER = "researcher"
    ADVOCATE = "advocate"
    JUDGE = "judge"
    ADMIN = "admin"


class Act(Base):
    __tablename__ = "acts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    short_title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    long_title: Mapped[str] = mapped_column(Text, nullable=False)
    act_no: Mapped[Optional[str]] = mapped_column(String(64))
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    jurisdiction: Mapped[ActJurisdiction] = mapped_column(
        Enum(ActJurisdiction), default=ActJurisdiction.INDIA_CENTRAL, nullable=False
    )
    status: Mapped[ActStatus] = mapped_column(Enum(ActStatus), default=ActStatus.IN_FORCE, nullable=False, index=True)
    replaces_act_id: Mapped[Optional[int]] = mapped_column(ForeignKey("acts.id", ondelete="SET NULL"))
    replaced_by_act_id: Mapped[Optional[int]] = mapped_column(ForeignKey("acts.id", ondelete="SET NULL"))
    source_pdf: Mapped[Optional[str]] = mapped_column(String(1024))
    source_url: Mapped[Optional[str]] = mapped_column(String(1024))
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64))
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sections: Mapped[list["Section"]] = relationship(
        back_populates="act", cascade="all, delete-orphan", foreign_keys="Section.act_id"
    )


class Section(Base):
    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint("act_id", "section_number", name="uq_act_section_number"),
        Index("ix_sections_act_id_section_number", "act_id", "section_number"),
        Index("ix_sections_keywords", "keywords", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    part: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    section_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    bare_text: Mapped[str] = mapped_column(Text, nullable=False)
    plain_language: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    punishments: Mapped[Optional[str]] = mapped_column(Text)
    bailable: Mapped[Optional[bool]] = mapped_column(Boolean)
    cognizable: Mapped[Optional[bool]] = mapped_column(Boolean)
    compoundable: Mapped[Optional[bool]] = mapped_column(Boolean)
    fine_min: Mapped[Optional[float]] = mapped_column(Float)
    fine_max: Mapped[Optional[float]] = mapped_column(Float)
    imprisonment_min_months: Mapped[Optional[int]] = mapped_column(Integer)
    imprisonment_max_months: Mapped[Optional[int]] = mapped_column(Integer)
    death_penalty: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    life_imprisonment: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    source_pdf: Mapped[Optional[str]] = mapped_column(String(1024))
    source_page: Mapped[Optional[int]] = mapped_column(Integer)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64))
    vector_version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    act: Mapped["Act"] = relationship(back_populates="sections", foreign_keys=[act_id])
    outgoing_relations: Mapped[list["KGRelation"]] = relationship(
        back_populates="source_section", foreign_keys="KGRelation.source_section_id"
    )
    incoming_relations: Mapped[list["KGRelation"]] = relationship(
        back_populates="target_section", foreign_keys="KGRelation.target_section_id"
    )
    ipc_bns_out: Mapped[list["IPCBNSMapping"]] = relationship(
        back_populates="source_section", foreign_keys="IPCBNSMapping.source_section_id"
    )
    ipc_bns_in: Mapped[list["IPCBNSMapping"]] = relationship(
        back_populates="target_section", foreign_keys="IPCBNSMapping.target_section_id"
    )


class IPCBNSMapping(Base):
    __tablename__ = "ipc_bns_mappings"
    __table_args__ = (
        UniqueConstraint("source_section_id", "target_section_id", "mapping_kind", name="uq_ipc_bns_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mapping_kind: Mapped[str] = mapped_column(
        String(32),
        default="ipc_to_bns",
        nullable=False,
        index=True,
        doc="ipc_to_bns | bns_to_ipc | analogous",
    )
    equivalence: Mapped[str] = mapped_column(
        String(32),
        default="exact",
        nullable=False,
        doc="exact | partial | expanded | narrowed | split | merged",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source_section: Mapped["Section"] = relationship(
        back_populates="ipc_bns_out", foreign_keys=[source_section_id]
    )
    target_section: Mapped["Section"] = relationship(
        back_populates="ipc_bns_in", foreign_keys=[target_section_id]
    )


class KGRelation(Base):
    __tablename__ = "kg_relations"
    __table_args__ = (
        UniqueConstraint("source_section_id", "target_section_id", "relation_type", name="uq_kg_edge"),
        Index("ix_kg_type", "relation_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation_type: Mapped[KGRelationType] = mapped_column(Enum(KGRelationType), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=0.8, server_default="0.8")
    evidence: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source_section: Mapped["Section"] = relationship(
        back_populates="outgoing_relations", foreign_keys=[source_section_id]
    )
    target_section: Mapped["Section"] = relationship(
        back_populates="incoming_relations", foreign_keys=[target_section_id]
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.RESEARCHER, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BenchmarkQuestion(Base):
    __tablename__ = "benchmark_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(64), default="retrieval", index=True)
    difficulty: Mapped[str] = mapped_column(String(32), default="medium", index=True)
    relevant_section_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    ideal_answer: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recall_at_5: Mapped[Optional[float]] = mapped_column(Float)
    recall_at_10: Mapped[Optional[float]] = mapped_column(Float)
    precision_at_10: Mapped[Optional[float]] = mapped_column(Float)
    mrr: Mapped[Optional[float]] = mapped_column(Float)
    hallucination_rate: Mapped[Optional[float]] = mapped_column(Float)
    num_questions: Mapped[int] = mapped_column(Integer, default=0)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


_REGISTRY = (Act, Section, IPCBNSMapping, KGRelation, User, BenchmarkQuestion, BenchmarkRun)
