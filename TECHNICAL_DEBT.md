
# Nyaya AI - Technical Debt Inventory

## Overview
All technical debt items are documented here, with priority (P0-P3), impact, and remediation steps!

---

## 📊 Debt Items

| ID | Item | Priority | Impact | Remediation Steps |
|----|------|----------|--------|--------------------|
| TD-001 | Duplicate embedding scripts (`embed_sections.py` and `embed_all_sections.py` exist with overlapping functionality) | P1 | Confusion about which script to use, maintenance overhead | Keep `embed_all_sections.py` as primary, delete or deprecate `embed_sections.py` |
| TD-002 | Temporary debug/test files in project root (`debug_parser.py`, `test_sanity.py`) | P2 | Clutters repo, violates clean architecture | Move to `backend/scripts/debug/` or delete if no longer needed |
| TD-003 | Dockerfile copies incorrect scripts directory (tries to copy top-level `scripts/` but scripts are in `backend/scripts/`) | P0 | Prevents pipeline execution in Docker container | Fix Dockerfile COPY command to use `backend/scripts` instead of `scripts` |
| TD-004 | No automated test suite | P0 | 0% test coverage, no regression safety | Add comprehensive unit/integration/API tests, target 90%+ coverage |
| TD-005 | No dedicated OCR libraries or fallback logic (Phase 3 requirement) | P1 | Cannot handle scanned PDFs | Add tesseract, ocrmypdf dependencies and OCR fallback in `parsers.py` |
| TD-006 | No progress tracking or retry logic in ingestion pipeline | P1 | No observability, no failure recovery | Add tqdm, tenacity for retries, structured logging in pipeline |
| TD-007 | No citation engine implementation (Phase 8) | P1 | Answers don't include verifiable citations | Implement citation extraction and verification |
| TD-008 | No hallucination protection (Phase 9) | P0 | Risk of fabricated legal answers | Add confidence scoring, source verification, claim detection |
| TD-009 | No benchmark dataset for RAG evaluation (Phase 7) | P2 | Cannot measure RAG quality | Create 500+ legal question benchmark |
| TD-010 | No comprehensive CI/CD pipeline (Phase 12) | P1 | No automated quality checks | Expand GitHub Actions to run all tests/scans/validations |

---

## 📉 Debt Summary
- P0: 3 items
- P1: 4 items
- P2: 3 items

---
## 📅 Remediation Plan
1. **P0 first**: Fix Dockerfile COPY command, implement hallucination protection, add test suite
2. **P1 next**: Resolve duplicate scripts, add OCR, add pipeline features, citation engine
3. **P2 last**: Clean up root files, create benchmark, expand CI/CD
