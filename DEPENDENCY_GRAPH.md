
# Nyaya AI - Dependency Graph

## Overview
This document outlines all dependencies for the Nyaya AI legal platform, organized by service and component.

---

## 🌐 Backend Dependencies (FastAPI)

### Core Web Framework
- fastapi == 0.115.0
- uvicorn[standard] == 0.30.6
- slowapi == 0.1.9
- limits == 3.13.0

### Database
- sqlalchemy[asyncio] == 2.0.36
- asyncpg == 0.30.0
- alembic == 1.14.0

### Configuration & Auth
- pydantic-settings == 2.6.1
- firebase-admin == 6.6.0
- python-dotenv == 1.0.1
- python-jose[cryptography] == 3.3.0
- passlib[bcrypt] == 1.7.4
- bcrypt == 4.1.2

### Caching & Messaging
- redis == 5.2.0

### Vector Database
- qdrant-client == 1.12.0

### AI/LLM Integrations
- groq == 0.28.0
- google-generativeai == 0.8.3
- cerebras-cloud-sdk == 1.19.0
- sentence-transformers == 3.3.1 (local embeddings)

### Data Ingestion
- pdfplumber == 0.11.4
- beautifulsoup4 == 4.12.3
- lxml == 5.3.0
- tqdm == 4.67.0
- langdetect == 1.0.9

### HTTP Clients
- httpx == 0.28.0
- aiohttp == 3.11.0

### Utilities
- python-multipart == 0.0.12

### Testing
- pytest == 8.3.3
- pytest-asyncio == 0.24.0

---

## 🖥️ Frontend Dependencies (Next.js)
Based on `frontend/package.json` (inferred from standard Next.js setups, will update with actual scan later):
- Next.js 15+
- React 19
- Tailwind CSS
- Lucide Icons
- Firebase (client-side auth)

---

## 🐳 Infrastructure Dependencies (Docker)
- postgres:16-alpine
- redis:7-alpine
- qdrant/qdrant:v1.12.5
- prometheus, grafana (monitoring)

---

## 🔄 Dependencies to be Added (Phases 3‑17)
- OCR libraries (tesseract, ocrmypdf)
- Benchmarking tools (locust, pytest-benchmark)
- Security tools (git-secrets, trivy for container scans)
- Observability (opentelemetry, loki, alertmanager)
