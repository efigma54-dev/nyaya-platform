# Enterprise Engineering Roadmap: Phases 1-17

**Current Achievement:** 9.0/10  
**Target Achievement:** 9.9-10/10  
**Timeline:** 12 weeks  
**Status:** Phase 1 Complete, Phases 2-17 Documented

---

## Phase Completion Status

| Phase | Name | Status | Effort | Payoff |
|-------|------|--------|--------|--------|
| 1 | Repository Audit | ✅ COMPLETE | 1 day | Baseline clarity |
| 2 | Enterprise Corpus | 🔜 START | 3 weeks | +0.2 (→ 9.2) |
| 3 | Ingestion Pipeline | 🔜 START | 2 weeks | +0.1 (→ 9.3) |
| 4 | Legal Chunking | 🔜 START | 1 week | +0.05 (→ 9.35) |
| 5 | Deduplication | 🔜 START | 3 days | +0.05 (→ 9.4) |
| 6 | Validation Framework | 🔜 IMPROVE | 1 week | Operational (→ 9.45) |
| 7 | Automatic Reports | 🔜 CONSOLIDATE | 2 days | Clarity (→ 9.5) |
| 8 | Benchmark Suite | 🔜 START | 1 week | +0.15 (→ 9.65) |
| 9 | Citation Engine | 🔜 START | 3 days | +0.1 (→ 9.75) |
| 10 | Hallucination Detection | 🔜 START | 3 days | +0.05 (→ 9.8) |
| 11 | Testing (90%+ coverage) | 🔜 EXPAND | 2 weeks | +0.05 (→ 9.85) |
| 12 | Security Hardening | 🔜 IMPLEMENT | 1 week | +0.05 (→ 9.9) |
| 13 | Observability Stack | 🔜 DEPLOY | 1 week | Operational |
| 14 | Performance Tuning | 🔜 OPTIMIZE | 1 week | +0.02 (→ 9.92) |
| 15 | CI/CD Pipeline | 🔜 AUTOMATE | 1 week | Operational |
| 16 | Documentation | 🔜 COMPLETE | 1 week | Operational |
| 17 | Acceptance Gates | 🔜 VALIDATE | 2 days | Final check |

---

## Phase 2: Enterprise Legal Corpus (3 weeks)

**Objective:** Expand from 433 sections to 1000+ sections with complete metadata

### Deliverables
```
✓ Constitution of India (395 articles + full text)
✓ BNS 2023 (511 sections)
✓ BNSS 2023 (531 sections)  
✓ BSA 2023 (167 sections)
✓ Central Acts (100+ acts, 1000+ sections)
✓ State Acts (28 states, 500+ sections)
✓ Rules & Notifications (200+)
✓ Supreme Court judgments (100+ landmark cases)
✓ High Court judgments (50+ per major HC)
```

### Data Structure
```python
Legal Document:
  - id: UUID
  - title: str
  - short_title: str
  - year: int
  - document_type: enum (ACT, RULE, NOTIFICATION, JUDGMENT)
  - sections: List[Section]
  - amendments: List[Amendment]
  - effective_date: datetime
  - source_url: str
  - sha256: str  # Deduplication
  - keywords: List[str]
  - metadata: dict
```

### Implementation Steps
1. Procure legal documents from IndiaCode.nic.in, SCC Online, AIR, etc.
2. Parse PDFs with OCR fallback
3. Structure into legal hierarchy
4. Validate against duplicates
5. Enrich with metadata
6. Embed vectors (5000+ vectors)
7. Seed PostgreSQL + Qdrant

---

## Phase 3: Enterprise Ingestion Pipeline (2 weeks)

**Objective:** Production-grade ingestion with retry, resume, deduplication

### Pipeline Flow
```
Input PDF → OCR (Tesseract fallback) → Parser
    ↓
Validator (schema check) → Deduplicator (SHA256)
    ↓
Chunker (legal structure) → Metadata Enricher
    ↓
Embedding (batch) → Qdrant Insert
    ↓
PostgreSQL Insert → Validation Report
```

### Key Features
- Multiprocessing (4 workers)
- Checkpoint/resume capability
- Retry with exponential backoff
- Comprehensive logging
- Progress tracking (tqdm)
- Deduplication at 3 levels:
  - Content hash (SHA256)
  - Embedding similarity (cosine >0.99)
  - Metadata (act_id + section_number)

### Deliverables
```
backend/ingestion/
├── pipeline.py         (orchestrator)
├── parser.py           (document parsing)
├── validator.py        (schema validation)
├── deduplicator.py     (hash + embedding)
├── chunker.py          (legal structure)
├── enricher.py         (metadata)
├── embedder.py         (vector generation)
├── upserter.py         (DB + Qdrant)
└── reporter.py         (pipeline reports)
```

---

## Phase 4: Legal Chunking (1 week)

**Objective:** Recognize legal structure and preserve hierarchy

### Recognition Rules
```python
Recognize:
  - Chapter/Part (e.g., "Part III")
  - Section (e.g., "Section 300")
  - Subsection (e.g., "Section 300(1)")
  - Clause (e.g., "Clause (a)")
  - Explanation (following section)
  - Illustration (example cases)
  - Exception (provided that...)
  - Proviso (specific conditions)
  - Schedule (appendix content)

Preserve Hierarchy:
  Document
    └── Part
        └── Chapter
            └── Section
                ├── Subsection
                ├── Explanation
                ├── Illustration
                ├── Exception
                └── Proviso
```

### Deliverables
```
backend/ingestion/chunker.py
  ├── detect_structure()
  ├── parse_hierarchy()
  ├── extract_explanation()
  ├── extract_illustration()
  └── validate_chunk_boundaries()
```

---

## Phase 5: Deduplication (3 days)

**Objective:** Prevent duplicate content at multiple levels

### Deduplication Strategy
```
Level 1: Content Hash (SHA256)
  - Hash every 1000-char chunk
  - Compare against existing hashes
  - Reject if match > 90%

Level 2: Embedding Similarity (Cosine)
  - Generate embeddings for new chunks
  - Query Qdrant for similar vectors
  - Reject if similarity > 0.99

Level 3: Metadata Deduplication
  - Check act_id + section_number combination
  - Reject if exact match exists
  - Flag for manual review if similar
```

### Deliverables
```
backend/ingestion/deduplicator.py
  ├── content_hash_check()
  ├── embedding_similarity_check()
  ├── metadata_check()
  ├── generate_dedup_report()
  └── deduplicated_document_count

deduplication_report.json
  ├── total_documents_processed
  ├── duplicates_detected
  ├── duplicates_by_level
  └── unique_content_added
```

---

## Phase 6: Validation Framework (1 week)

**Objective:** Consolidate validators into single framework

### Collectors (Already Exist - Consolidate)
```
backend/validation/collectors/
├── docker.py         ✅ (verify health status)
├── postgres.py       ✅ (verify schema, counts)
├── redis.py          ✅ (verify connectivity)
├── qdrant.py         ✅ (verify collections)
├── fastapi.py        ✅ (verify endpoints)
├── git.py            ✅ (verify commit)
├── security.py       🔜 (Bandit, pip-audit)
├── tests.py          🔜 (coverage %)
├── rag.py            ✅ (corpus stats)
└── corpus.py         ✅ (duplicate check)
```

### Consolidation
- Merge 18 report files into 1 validation.json
- Remove manual edits
- Add version tracking
- Add timestamp
- Add git commit SHA

---

## Phase 7: Automatic Reports (2 days)

**Objective:** Single source of truth for system status

### Report Generation (Automated)
```
validation.json
├── timestamp: ISO8601
├── git_commit: SHA
├── version: semver
├── environment: dev/staging/prod
├── docker:
│   ├── postgres: healthy/unhealthy
│   ├── redis: healthy/unhealthy
│   ├── qdrant: healthy/unhealthy
│   ├── api: healthy/unhealthy
│   └── frontend: healthy/unhealthy
├── database:
│   ├── acts: COUNT(*)
│   ├── sections: COUNT(*)
│   ├── vectors: COUNT(*)
│   └── sync_percentage: 100%
├── security:
│   ├── bandit_score: A/B/C/D/E
│   ├── pip_audit_issues: 0
│   ├── trivy_issues: 0
│   └── secrets_found: false
├── tests:
│   ├── coverage: 92%
│   ├── unit_tests: PASS
│   ├── integration_tests: PASS
│   └── performance_tests: PASS
├── benchmarks:
│   ├── recall_at_5: 95%
│   ├── precision: 92%
│   ├── latency_p95: 500ms
│   └── hallucination_rate: 1.2%
└── overall_score: 9.5/10
```

### Output Formats
```
✓ validation.json    (machine-readable)
✓ validation.md      (human-readable)
✓ validation.html    (dashboard)
✓ dashboard.html     (interactive)
```

---

## Phase 8: Benchmark Suite (1 week)

**Objective:** 1000 legal questions covering all domains

### Coverage
```
Criminal:         200 questions (BNS, BNSS, BSA)
Civil:            200 questions (Contracts, property, family)
Constitutional:   100 questions (Fundamental rights, duties)
Evidence:         100 questions (Proof, witnesses, documents)
Family:           100 questions (Marriage, divorce, inheritance)
Labour:           100 questions (Employment, wages, disputes)
Cyber:            100 questions (IT Act, cyber crimes)
GST:              50 questions (Tax, registration, returns)
Consumer:         50 questions (Complaints, refunds, liability)
Property:         50 questions (Transfer, ownership, disputes)
Motor Vehicle:    50 questions (Accidents, insurance, fines)
POCSO:            50 questions (Child protection, offences)
RTI:              50 questions (Information, appeals)
DV:               50 questions (Domestic violence, protection)
```

### Metrics
```
For each question:
  - question_id: unique
  - question_text: str
  - domain: enum
  - expected_sections: List[str]
  - golden_answer: str
  - difficulty: easy/medium/hard

Measure:
  - Recall@5: % of expected sections in top 5 results
  - Recall@10: % of expected sections in top 10 results
  - Precision: exactness of retrieved sections
  - MRR: mean reciprocal rank
  - Citation Accuracy: all sections properly cited
  - Hallucination Rate: % of unsupported claims
  - Latency: ms to respond
```

### Deliverables
```
backend/benchmarks/
├── benchmark_questions.json      (1000 questions)
├── benchmark_runner.py           (execution)
├── benchmark_results.json        (results)
├── benchmark_report.html         (visualization)
└── benchmark_history/            (tracking over time)
```

---

## Phase 9: Citation Engine (3 days)

**Objective:** Every response cites actual sections

### Implementation
```python
class CitationEngine:
    def cite_response(self, answer: str, retrieved_chunks: List[Chunk]) -> Citation:
        """Extract claims and map to sources."""
        return Citation(
            act: str,
            section: str,
            subsection: Optional[str],
            source: str,
            confidence: float,  # 0-1
            chunk_id: str,
            effective_date: datetime,
            amendment_status: str
        )
    
    def validate_citation(self, citation: Citation) -> bool:
        """Verify citation actually exists in database."""
        pass
    
    def reject_unsupported(self, answer: str) -> bool:
        """Reject if no supporting sections found."""
        pass
```

### Response Format
```json
{
    "answer": "Murder is defined in Section 300 BNS as...",
    "citations": [
        {
            "act": "BNS",
            "section": 300,
            "confidence": 0.98,
            "source_chunk_id": "abc123",
            "effective_date": "2024-07-01"
        }
    ],
    "grounded": true,
    "confidence_score": 0.95
}
```

---

## Phase 10: Hallucination Detection (3 days)

**Objective:** Automatically detect false claims

### Detection Strategy
```python
def detect_hallucination(answer: str, retrieved_sections: List[Section]) -> HallucinationReport:
    """
    1. Extract claims from answer
    2. For each claim, find supporting section
    3. If match score < 0.6, flag as hallucination
    4. Generate report
    """
    return HallucinationReport(
        total_claims: int,
        grounded_claims: int,
        hallucinated_claims: List[str],
        confidence_score: float,  # 0-1
        recommendation: str
    )
```

### Deliverables
```
backend/hallucination_detector.py
hallucination_report.json
```

---

## Phases 11-17 (Remaining Work)

**Phase 11:** 90%+ test coverage (unit, integration, API, Docker, migration)  
**Phase 12:** Security scanning (Bandit, pip-audit, Trivy, OWASP ZAP)  
**Phase 13:** Observability (Prometheus, Grafana, Loki, OpenTelemetry)  
**Phase 14:** Performance optimization (embedding batching, async DB, caching)  
**Phase 15:** Automated CI/CD pipeline (GitHub Actions)  
**Phase 16:** Complete documentation (architecture, API, schema, deployment)  
**Phase 17:** Acceptance gates (all checks must pass before deployment)  

---

## Success Criteria

### To Reach 9.9/10
```
✓ 1000+ sections in corpus
✓ 5000+ vectors embedded
✓ 100% DB ↔ Qdrant sync
✓ Benchmark recall@5 > 95%
✓ Benchmark precision > 90%
✓ Hallucination rate < 2%
✓ Response latency p95 < 500ms
✓ 90%+ test coverage
✓ Security score A+
✓ Zero High/Critical vulnerabilities
✓ All automation working
```

### To Reach 10/10
```
Above + ALL of:
✓ 1500+ sections
✓ Hallucination rate < 1%
✓ Citation accuracy 99%+
✓ Benchmark recall@5 > 97%
✓ Benchmark precision > 93%
✓ Performance optimized (p95 < 300ms)
✓ 95%+ test coverage
✓ 99.9% uptime in staging
✓ Complete documentation
✓ All acceptance gates pass
```

---

## Timeline & Resources

**Duration:** 12 weeks  
**Team:** 2-3 senior engineers  
**Estimated Cost:** $40-60K  
**Go-live:** August 30, 2026  

---

**Next:** Execute Phases 2-3 (Corpus Expansion + Ingestion Pipeline)

