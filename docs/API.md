# BALE API Documentation

## Overview

The BALE REST API provides programmatic access to contract analysis, simulation, and management features.

**Base URL:** `http://localhost:8080`  
**API Version:** v1

---

## Authentication

### JWT Token

Obtain a token via login:

```bash
POST /v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Use the token in subsequent requests:
```bash
curl -H "Authorization: Bearer eyJ..." http://localhost:8080/v1/analyze
```

### API Key

For service-to-service integrations:

```bash
curl -H "X-API-Key: bale_pk_..." http://localhost:8080/v1/analyze
```

---

## Rate Limits

| Plan | Requests/min | Requests/day |
|:-----|:-------------|:-------------|
| Free | 10 | 100 |
| Pro | 60 | 5,000 |
| Enterprise | 300 | Unlimited |

Rate limit headers:
```
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1705384800
```

---

## Endpoints

### Analysis

#### Analyze Clause

Analyze a contract clause for litigation risk.

```http
POST /v1/analyze
```

**Request Body:**

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `clause_text` | string | Yes | The clause to analyze (min 20 chars) |
| `jurisdiction` | string | No | Target jurisdiction (default: INTERNATIONAL) |
| `depth` | string | No | Analysis depth: `quick`, `standard`, `deep` |
| `include_harmonization` | bool | No | Include improvement suggestions |

**Example:**
```json
{
  "clause_text": "The Supplier shall not be liable for any indirect, incidental, special, consequential, or punitive damages...",
  "jurisdiction": "UK",
  "depth": "standard",
  "include_harmonization": true
}
```

**Response:**
```json
{
  "id": "ana_abc123",
  "verdict": {
    "risk_score": 65,
    "verdict": "PLAINTIFF_FAVOR",
    "confidence": 0.87,
    "factors_applied": [
      {
        "rule": "Contra Proferentem",
        "triggered": true,
        "impact": 15,
        "evidence": "Clause uses undefined term 'reasonable'"
      }
    ],
    "interpretive_gap": 25,
    "civilist_summary": "Under French law, Art. 1170 C.civ...",
    "commonist_summary": "English courts would apply UCTA 1977...",
    "synthesis": "Cross-jurisdictional analysis reveals..."
  },
  "harmonization": {
    "golden_clause": "Improved clause text...",
    "rationale": "Changes address identified risks...",
    "risk_reduction": 25
  },
  "processing_time_ms": 2340
}
```

#### Stream Analysis (SSE)

Get real-time progress updates:

```http
GET /v1/analyze/{analysis_id}/stream
Accept: text/event-stream
```

**Events:**
```
event: analysis_progress
data: {"stage": "civilist", "progress": 25}

event: analysis_agent
data: {"agent": "Civilist", "output": "..."}

event: analysis_completed
data: {"result": {...}}
```

---

### Simulation

#### Run Mock Trial

Simulate adversarial litigation scenarios.

```http
POST /v1/simulate
```

**Request Body:**
```json
{
  "clause_text": "Force majeure clause...",
  "scenario": "pandemic",
  "jurisdiction": "INTERNATIONAL",
  "plaintiff_strategy": "aggressive"
}
```

**Response:**
```json
{
  "id": "sim_xyz789",
  "outcome": "PLAINTIFF_WINS",
  "probability": 0.72,
  "arguments": {
    "plaintiff": [...],
    "defense": [...]
  },
  "key_vulnerabilities": [...],
  "recommendations": [...]
}
```

---

### Contracts

#### List Contracts

```http
GET /v1/contracts?page=1&limit=20&status=active
```

**Query Parameters:**

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `page` | int | Page number (default: 1) |
| `limit` | int | Items per page (default: 20, max: 100) |
| `status` | string | Filter by status: `active`, `archived` |
| `jurisdiction` | string | Filter by jurisdiction |

**Response:**
```json
{
  "items": [
    {
      "id": "con_123",
      "name": "SaaS Master Agreement",
      "jurisdiction": "UK",
      "status": "active",
      "risk_score": 45,
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "total": 156,
  "page": 1,
  "pages": 8
}
```

#### Create Contract

```http
POST /v1/contracts
```

**Request Body:**
```json
{
  "name": "New Contract",
  "content": "Full contract text...",
  "jurisdiction": "UK"
}
```

#### Get Contract

```http
GET /v1/contracts/{id}
```

#### Update Contract

```http
PATCH /v1/contracts/{id}
```

```json
{
  "name": "Updated Name",
  "status": "archived"
}
```

#### Delete Contract

```http
DELETE /v1/contracts/{id}
```

---

### Webhooks

#### Register Webhook

```http
POST /v1/webhooks
```

```json
{
  "url": "https://your-server.com/webhook",
  "events": ["analysis.completed", "risk.high_detected"],
  "secret": "your_webhook_secret"
}
```

**Event Types:**
- `analysis.started`
- `analysis.completed`
- `analysis.failed`
- `risk.high_detected`
- `contract.created`
- `contract.updated`

**Webhook Payload:**
```json
{
  "id": "evt_123",
  "type": "analysis.completed",
  "timestamp": "2026-01-16T00:00:00Z",
  "data": {
    "analysis_id": "ana_123",
    "risk_score": 72
  }
}
```

**Signature Verification:**
```python
import hmac
import hashlib

def verify_webhook(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

### Analytics

#### Get Dashboard Data

```http
GET /v1/analytics/dashboard
```

**Response:**
```json
{
  "summary": {
    "total_analyses": 1234,
    "avg_risk_score": 42.5,
    "high_risk_count": 89
  },
  "risk_trend": [
    {"date": "2026-01-10", "risk": 45},
    {"date": "2026-01-11", "risk": 42}
  ],
  "jurisdiction_breakdown": {
    "UK": {"count": 450, "avg_risk": 38},
    "US": {"count": 320, "avg_risk": 45}
  }
}
```

#### Generate Report

```http
POST /v1/analytics/report
```

```json
{
  "format": "pdf",
  "time_range": "30d"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Clause text must be at least 20 characters",
    "details": {
      "field": "clause_text",
      "constraint": "min_length"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|:-----|:------------|:------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## SDKs

### Python

```python
from bale import BaleClient

client = BaleClient(api_key="bale_pk_...")

result = client.analyze(
    clause_text="...",
    jurisdiction="UK"
)

print(f"Risk: {result.risk_score}%")
```

### JavaScript

```javascript
import { BaleClient } from '@bale/sdk';

const client = new BaleClient({ apiKey: 'bale_pk_...' });

const result = await client.analyze({
  clauseText: '...',
  jurisdiction: 'UK'
});

console.log(`Risk: ${result.riskScore}%`);
```

---

## OpenAPI Spec

Full OpenAPI specification available at:
- **Swagger UI:** `http://localhost:8080/docs`
- **ReDoc:** `http://localhost:8080/redoc`
- **JSON:** `http://localhost:8080/openapi.json`
