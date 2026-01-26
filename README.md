# BALE - Binary Adjudication & Litigation Engine

<div align="center">

![BALE Logo](https://img.shields.io/badge/BALE-V8_Ultimate-black?style=for-the-badge)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg?style=flat-square)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-Research-red.svg?style=flat-square)](research/paper.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18377733.svg)](https://doi.org/10.5281/zenodo.18377733)

**A neuro-symbolic legal reasoning engine for auditing international commercial contracts.**

📄 **[Research Paper](research/paper.md)** • [Quick Start](#-quick-start) • [API Docs](#-api-reference) • [Cite](#-citation)

</div>

---

## 📚 Research Paper

> **BALE: A Neuro-Symbolic Framework for Bilingual Contract Risk Assessment**
> 
> Hamza Masmoudi (Independent Researcher), 2026

### Key Results

| Metric | Score |
|--------|-------|
| Clause Type Accuracy | **97.8%** |
| Risk Detection | **65.9%** (+21% over baseline) |
| Languages | English + French |
| Training Data | 75,382 examples |

📄 **Full Paper**: [research/paper.md](research/paper.md)

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



## 📸 Interface

![BALE Landing Page](docs/images/bale_landing.png)

![BALE Dashboard](docs/images/bale_dashboard.png)

---

## 🎯 Overview

BALE is an enterprise-grade AI system that analyzes commercial contracts for litigation risk. It combines:

- **Neuro-Symbolic Reasoning**: LLM interpretation + deterministic legal rules
- **Multi-Jurisdiction Support**: UK, France, US, Germany, EU, Singapore
- **Explainable Decisions**: Full audit trail with legal citations
- **Production Ready**: REST API, authentication, caching, webhooks

### Key Capabilities

| Feature | Description |
|:--------|:------------|
| **Clause Analysis** | Deep analysis of contract clauses with risk scoring |
| **Mock Trial Simulation** | Adversarial scenario planning |
| **Harmonization** | AI-suggested clause improvements |
| **Multi-Jurisdiction** | Compare interpretations across legal systems |
| **Knowledge Graph** | Citation tracking and precedent analysis |

### 🚀 V8 Ultimate - Production-Ready Legal AI

BALE V8 Ultimate is trained on **75,381 real legal examples** from 10 sources, powered by fine-tuned **Mistral-7B** with LoRA:

| Metric | Score | Description |
|:-------|:-----:|:------------|
| **English Classification** | 66.7% | Identify clause types (indemnification, liability, etc.) |
| **Risk Detection** | 66.7% | Detect HIGH/MEDIUM/LOW risk clauses |
| **Edge Cases** | 80.0% | Handle varied input formats |
| **Latency** | ~1.2s | Production-ready inference |

**Training Data (75K+ examples):**
| Source | Examples |
|:-------|:--------:|
| CUAD (SEC contracts) | 10,667 |
| Legal Argument Mining | 23,113 |
| Claudette ToS | 9,319 |
| Mistral Legal French | 14,875 |
| EURLex-4K | 5,000 |
| + 5 more sources | ~13,000 |

**API Endpoints:**
```bash
# Clause Analysis
POST /api/v8/analyze/clause
{"clause_text": "Provider shall have no liability whatsoever..."}

# Full Contract Analysis  
POST /api/v8/analyze/contract
{"contract_text": "[full contract text]"}

# List All Clause Types (75 types)
GET /api/v8/clause-types
```


---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 20+ (for frontend)
- 32GB+ RAM recommended for local LLM

### 1. Clone & Setup

```bash
git clone https://github.com/yourorg/bale-project.git
cd bale-project

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
# Start infrastructure (PostgreSQL, Redis, Neo4j)
docker-compose up -d postgres redis neo4j

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

## 📖 API Reference

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
    "factors_applied": [...]
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
GET    /v1/contracts           # List contracts
POST   /v1/contracts           # Create contract
GET    /v1/contracts/{id}      # Get contract
PATCH  /v1/contracts/{id}      # Update contract
DELETE /v1/contracts/{id}      # Delete contract
```

#### WebSocket (Real-time)
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/user_123');
ws.send(JSON.stringify({ action: 'subscribe', analysis_id: 'ana_123' }));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (3000)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (8080)                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │  Auth   │  │  Cache  │  │Webhooks │  │  Analytics  │    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│    LangGraph     │ │   Vector Store   │ │   Knowledge      │
│    Pipeline      │ │   (ChromaDB)     │ │   Graph (Neo4j)  │
│                  │ │                  │ │                  │
│  ┌────────────┐  │ │  Hybrid Search   │ │  Citations       │
│  │  Civilist  │  │ │  + Authority     │ │  Precedents      │
│  │  Commonist │  │ │    Boosting      │ │  Equivalence     │
│  │  Synthesizer│ │ │                  │ │                  │
│  │  Judge     │  │ │                  │ │                  │
│  └────────────┘  │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                    LLM Backend                              │
│  ┌─────────────────┐    ┌─────────────────────────────┐     │
│  │  Local (Ollama) │ OR │  Cloud (Mistral, DeepSeek)  │     │
│  │  Qwen 32B       │    │                             │     │
│  └─────────────────┘    └─────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Agent Pipeline

1. **Ingestion**: PDF → Semantic chunks → Legal ontology tagging
2. **Retrieval**: Hybrid search with authority boosting
3. **Analysis**: Civilist + Commonist + IP Specialist interpretations
4. **Synthesis**: Cross-doctrine harmonization
5. **Simulation**: Adversarial mock trial
6. **Adjudication**: Deterministic risk scoring

---

## 🧠 Fine-Tuning

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

## 🐳 Docker Deployment

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

## 📊 Monitoring

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

## 🔐 Security

- JWT authentication with short-lived tokens
- API key support for service integrations
- Role-based access control (RBAC)
- Rate limiting per user/key
- Audit logging for compliance

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---


