from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import PydanticCustomError
from pydantic import field_validator

from nyaya.db.models.schema import KGRelationType, UserRole

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _validate_email(v: str) -> str:
    if not isinstance(v, str) or not _EMAIL_RE.match(v):
        raise PydanticCustomError("email_format", "Value is not a valid email address")
    return v


class ConfigBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)


class ActBase(ConfigBase):
    short_title: str
    long_title: str
    act_no: Optional[str] = None
    year: int
    jurisdiction: str = "india_central"
    status: str = "in_force"
    replaces_act_id: Optional[int] = None
    replaced_by_act_id: Optional[int] = None
    source_pdf: Optional[str] = None
    source_url: Optional[str] = None
    checksum_sha256: Optional[str] = None
    extra_data: dict[str, Any] = Field(default_factory=dict)


class ActOut(ActBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ActCreate(ActBase):
    pass


class SectionBase(ConfigBase):
    act_id: int
    chapter: Optional[str] = None
    part: Optional[str] = None
    section_number: str
    title: str
    bare_text: str
    plain_language: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    punishments: Optional[str] = None
    bailable: Optional[bool] = None
    cognizable: Optional[bool] = None
    compoundable: Optional[bool] = None
    fine_min: Optional[float] = None
    fine_max: Optional[float] = None
    imprisonment_min_months: Optional[int] = None
    imprisonment_max_months: Optional[int] = None
    death_penalty: bool = False
    life_imprisonment: bool = False
    source_pdf: Optional[str] = None
    source_page: Optional[int] = None
    checksum_sha256: Optional[str] = None
    extra_data: dict[str, Any] = Field(default_factory=dict)


class SectionOut(SectionBase):
    id: int
    vector_version: int
    created_at: datetime
    updated_at: datetime


class SectionOutWithAct(SectionOut):
    act_short_title: Optional[str] = None
    act_year: Optional[int] = None


class SectionCreate(SectionBase):
    pass


class IPCBNSMappingOut(ConfigBase):
    id: int
    source_section_id: int
    target_section_id: int
    mapping_kind: str
    equivalence: str
    notes: Optional[str] = None
    created_at: datetime


class IPCBNSMappingCreate(ConfigBase):
    source_section_id: int
    target_section_id: int
    mapping_kind: Literal["ipc_to_bns", "bns_to_ipc", "analogous"] = "ipc_to_bns"
    equivalence: Literal["exact", "partial", "expanded", "narrowed", "split", "merged"] = "exact"
    notes: Optional[str] = None


class IPCBNSCompare(ConfigBase):
    left: SectionOutWithAct
    right: SectionOutWithAct
    mapping: IPCBNSMappingOut
    plain_translation: Optional[str] = None


class KGRelationOut(ConfigBase):
    id: int
    source_section_id: int
    target_section_id: int
    relation_type: str
    weight: float
    evidence: Optional[str] = None
    created_at: datetime


class KGRelationCreate(ConfigBase):
    source_section_id: int
    target_section_id: int
    relation_type: KGRelationType
    weight: float = 0.8
    evidence: Optional[str] = None


class KGSubgraph(ConfigBase):
    nodes: list[SectionOutWithAct]
    edges: list[KGRelationOut]


class SearchResult(ConfigBase):
    section_id: int
    rank: int
    bm25_score: Optional[float] = None
    dense_score: Optional[float] = None
    rerank_score: Optional[float] = None
    combined_score: float
    citation_validated: bool
    citation_similarity: Optional[float] = None
    snippets: list[str] = Field(default_factory=list)
    section: Optional[SectionOutWithAct] = None


class SearchResponse(ConfigBase):
    query: str
    total: int
    latency_ms: int
    results: list[SearchResult]


class SearchQuery(ConfigBase):
    q: str
    top_k: int = Field(default=10, ge=1, le=100)
    include_bm25: bool = True
    include_dense: bool = True
    rerank: bool = True
    validate_citations: bool = True
    act_ids: Optional[list[int]] = None


class UserCreate(ConfigBase):
    email: str
    name: Optional[str] = None
    password: str
    role: UserRole = UserRole.RESEARCHER

    @field_validator("email")
    @classmethod
    def _v_email(cls, v): return _validate_email(v)


class UserLogin(ConfigBase):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _v_email(cls, v): return _validate_email(v)


class UserOut(ConfigBase):
    id: int
    email: str
    name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class TokenOut(ConfigBase):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class BenchmarkMetrics(ConfigBase):
    run_name: str
    num_questions: int
    recall_at_5: float
    recall_at_10: float
    precision_at_10: float
    mrr: float
    hallucination_rate: float
    details: dict[str, Any] = Field(default_factory=dict)


class HealthStatus(ConfigBase):
    status: str
    app_env: str
    postgres: str
    qdrant: str
    redis: str
    sections_count: int
    acts_count: int
    mappings_count: int
    questions_count: int
    timestamp: datetime
