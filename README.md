# BALE - Binary Adjudication & Litigation Engine

<div align="center">

![BALE](https://img.shields.io/badge/BALE-V10_Contract_Intelligence-black?style=for-the-badge)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg?style=flat-square)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-Research-red.svg?style=flat-square)](research/paper.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18377733.svg)](https://doi.org/10.5281/zenodo.18377733)

**A contract intelligence engine that detects inter-clause conflicts, power asymmetry, and dispute hotspots.**

[Research Paper](research/paper.md) | [Quick Start](#quick-start) | [API Docs](#api-reference) | [Cite](#citation)

</div>

---

## Research Paper

> **BALE: A Neuro-Symbolic Framework for Bilingual Contract Risk Assessment**
>
> Hamza Masmoudi (Independent Researcher), 2026

### Key Results

| Metric | V8 | V10 | Improvement |
|:-------|:---:|:---:|:---:|
| Overall Accuracy | 50.8% | **80.2%** | +29.4% |
| English Classification | 66.7% | **76.5%** | +9.8% |
| French Classification | 10.0% | **85.0%** | +75.0% |
| Latency | 1,241ms | **<5ms** | 250x faster |

**Full Paper**: [research/paper.md](research/paper.md)

### Citation

```bibtex
@software{masmoudi2026bale,
  author = {Masmoudi, Hamza},
  title = {BALE: A Neuro-Symbolic Framework for Bilingual Contract Risk Assessment},
  year = {2026},
  doi = {10.5281/zenodo.18377733},
  url = {https://github.com/hamza2masmoudi/BALE-project}
}
```

## Interface

![BALE Landing Page](docs/images/bale_landing.png)
![BALE Dashboard](docs/images/bale_dashboard.png)

---

## Overview

BALE is an AI system that analyzes commercial contracts for litigation risk. It combines:

- **Contract Reasoning Graph**: Models inter-clause relationships (conflicts, dependencies, gaps)
- **Power Asymmetry Detection**: Quantifies obligation imbalance between parties
- **Dispute Hotspot Prediction**: Identifies clauses most likely to be contested
- **Multilingual Support**: English and French via zero-shot embeddings
- **Production Ready**: REST API, authentication, caching, webhooks

### V10 Contract Intelligence Engine

BALE V10 replaces the fine-tuned LLM classifier with a zero-shot embedding approach and adds structural contract reasoning:

| Component | Description |
|:----------|:------------|
| **Embedding Classifier** | Zero-shot clause classification via cosine similarity (<5ms) |
| **Contract Graph** | 16 legal doctrinal relationships between clause types |
| **Power Analyzer** | Party-level obligation and protection scoring |
| **Dispute Predictor** | Per-clause dispute probability based on conflicts and asymmetry |

### Ablation Study

Each V10 layer contributes to risk detection (scores on representative contracts):

| Contract | Classifier | +Graph | +Power | Full V10 |
|:---------|:---:|:---:|:---:|:---:|
| Vendor Heavy MSA | 64.3 | 85.7 | 67.0 | 69.2 |
| AI Services MSA | 63.3 | 85.3 | 63.5 | 74.3 |
| Missing Clauses MSA | 58.9 | 83.6 | 62.9 | 70.3 |
| Cloud SLA | 63.0 | 85.2 | 62.6 | 68.1 |
| Standard NDA | 57.7 | 83.1 | 57.3 | 58.7 |

The Graph layer provides the largest marginal improvement (+10.7 avg), validating that inter-clause reasoning is the primary contribution.

### Training Data (75K+ examples)

| Source | Examples |
|:-------|:--------:|
| CUAD (SEC contracts) | 10,667 |
| Legal Argument Mining | 23,113 |
| Claudette ToS | 9,319 |
| Mistral Legal French | 14,875 |
| EURLex-4K | 5,000 |
| + 5 more sources | ~13,000 |

### API Endpoints

```bash
# Clause Analysis
POST /v1/analyze
{"clause_text": "Provider shall have no liability whatsoever..."}

# Full Contract Analysis
POST /v1/analyze/contract
{"contract_text": "[full contract text]"}

# List All Clause Types
GET /v1/clause-types
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 20+ (for frontend)
- 32GB+ RAM recommended for local LLM

### 1. Clone & Setup

```bash
git clone https://github.com/hamza2masmoudi/BALE-project.git
cd BALE-project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

Key variables:

```env
# LLM Configuration
LOCAL_LLM_ENDPOINT=http://localhost:11434/v1/chat/completions
LOCAL_LLM_MODEL=qwen2.5:32b
MISTRAL_API_KEY=your_key_here  # Optional fallback

# Database
DATABASE_URL=postgresql://bale:bale_dev@localhost:5432/bale
REDIS_URL=redis://localhost:6379/0

# Security
BALE_SECRET_KEY=your_secret_key_here
```

### 3. Start Services

```bash
# Start infrastructure (PostgreSQL, Redis)
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start API server
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Start Frontend (Optional)

```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8080/health

# Run tests
pytest tests/ -v
```

---

## API Reference

### Base URL

```
http://localhost:8080
```

### Authentication

BALE supports two authentication methods:

**JWT Bearer Token:**

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8080/v1/analyze
```

**API Key:**

```bash
curl -H "X-API-Key: bale_pk_..." http://localhost:8080/v1/analyze
```

### Endpoints

#### Analyze Clause

```http
POST /v1/analyze
Content-Type: application/json

{
  "clause_text": "The Supplier shall not be liable for indirect damages...",
  "jurisdiction": "UK",
  "depth": "standard",
  "include_harmonization": true
}
```

**Response:**

```json
{
  "id": "ana_123",
  "verdict": {
    "risk_score": 65,
    "verdict": "PLAINTIFF_FAVOR",
    "confidence": 0.87,
    "factors_applied": ["..."]
  },
  "harmonization": {
    "golden_clause": "Improved clause text...",
    "risk_reduction": 25
  }
}
```

#### Simulate Trial

```http
POST /v1/simulate
Content-Type: application/json

{
  "clause_text": "Force majeure clause...",
  "scenario": "pandemic",
  "jurisdiction": "INTERNATIONAL"
}
```

#### Contract CRUD

```http
GET    /v1/contracts       # List contracts
POST   /v1/contracts       # Create contract
GET    /v1/contracts/{id}  # Get contract
PATCH  /v1/contracts/{id}  # Update contract
DELETE /v1/contracts/{id}  # Delete contract
```

#### WebSocket (Real-time)

```javascript
const ws = new WebSocket('ws://localhost:8080/ws/user_123');
ws.send(JSON.stringify({ action: 'subscribe', analysis_id: 'ana_123' }));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## Architecture

```
+-------------------------------------------------------------+
|                   React Frontend (3000)                      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   FastAPI Backend (8080)                      |
|  +---------+  +---------+  +---------+  +-------------+     |
|  |  Auth   |  |  Cache  |  |Webhooks |  |  Analytics  |     |
|  +---------+  +---------+  +---------+  +-------------+     |
+-------------------------------------------------------------+
                              |
          +-------------------+-------------------+
          v                   v                   v
+------------------+  +------------------+  +------------------+
|   V10 Pipeline   |  |   Vector Store   |  |   Knowledge      |
|                  |  |   (ChromaDB)     |  |   Graph          |
|  Classifier      |  |                  |  |                  |
|  Contract Graph  |  |  Hybrid Search   |  |   Citations      |
|  Power Analyzer  |  |  + Authority     |  |   Precedents     |
|  Dispute Pred.   |  |  Boosting        |  |   Equivalence    |
+------------------+  +------------------+  +------------------+
                              |
                              v
+-------------------------------------------------------------+
|                  LLM Backend (Local First)                    |
|  +-----------------+  +-------------------------------+      |
|  | Local (Ollama)  |  | Dedicated Inference Node      |      |
|  | Qwen 32B       |  | (vLLM / MLX)                  |      |
|  +-----------------+  +-------------------------------+      |
+-------------------------------------------------------------+
```

### V10 Pipeline

1. **Chunking**: Contract text split into top-level sections
2. **Classification**: Zero-shot embedding classification (<5ms per clause)
3. **Graph Construction**: Map inter-clause relationships from legal doctrine
4. **Power Analysis**: Score obligation imbalance between parties
5. **Dispute Prediction**: Identify hotspot clauses with dispute probability
6. **Report Generation**: Structured JSON with risk scores and recommendations

---

## Fine-Tuning

BALE supports fine-tuning for domain adaptation:

```bash
# Generate training data
python -m training.dataset_curator generate --examples 1000

# Fine-tune (requires GPU)
python -m training.finetune \
  --preset llama-8b \
  --dataset ./training/output/legal_chatml.jsonl \
  --epochs 3 \
  --output ./models/bale-legal-v1
```

### Presets

| Preset | Base Model | VRAM | Speed |
|:-------|:-----------|:-----|:------|
| `qwen-32b` | Qwen2.5-32B-Instruct | 40GB+ | Slow |
| `llama-8b` | Llama-3.1-8B-Instruct | 16GB | Fast |
| `mistral-7b` | Mistral-7B-Instruct | 16GB | Fast |

---

## Docker Deployment

### Full Stack

```bash
docker-compose up -d
```

### Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Services

| Service | Port | Description |
|:--------|:-----|:------------|
| `api` | 8080 | FastAPI backend |
| `frontend` | 3000 | React dashboard |
| `postgres` | 5432 | PostgreSQL database |
| `redis` | 6379 | Caching layer |
| `neo4j` | 7474/7687 | Knowledge graph |

---

## Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

### Metrics

```bash
curl http://localhost:8080/metrics  # Prometheus format
```

### Logs

```bash
docker-compose logs -f api
```

---

## Security

- JWT authentication with short-lived tokens
- API key support for service integrations
- Role-based access control (RBAC)
- Rate limiting per user/key
- Audit logging for compliance

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request
