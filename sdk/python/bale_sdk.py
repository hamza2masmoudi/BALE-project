"""
BALE Python SDK
Client library for interacting with the BALE API.
"""
import os
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx
__version__ = "1.0.0"
# ==================== DATA CLASSES ====================
@dataclass
class DecisionFactor:
rule_name: str
description: str
triggered: bool
impact: int
evidence: str
@dataclass
class Verdict:
risk_score: int
verdict: str
confidence: float
factors: List[DecisionFactor]
interpretive_gap: int
civilist_summary: str
commonist_summary: str
@dataclass
class Harmonization:
golden_clause: str
rationale: str
risk_reduction: int
@dataclass
class AnalysisResult:
id: str
verdict: Verdict
harmonization: Optional[Harmonization]
processing_time_ms: int
# ==================== CLIENT ====================
class BaleClient:
"""
BALE API Client for Python.
Usage:
client = BaleClient(api_key="bale_pk_...")
result = client.analyze("Force majeure clause...", jurisdiction="UK")
print(f"Risk: {result.verdict.risk_score}%")
"""
def __init__(
self,
api_key: str = None,
base_url: str = None,
timeout: float = 120.0
):
"""
Initialize the BALE client.
Args:
api_key: BALE API key (or set BALE_API_KEY env var)
base_url: API base URL (default: http://localhost:8080)
timeout: Request timeout in seconds
"""
self.api_key = api_key or os.getenv("BALE_API_KEY")
self.base_url = (base_url or os.getenv("BALE_API_URL", "http://localhost:8080")).rstrip("/")
self.timeout = timeout
self._client = httpx.Client(
base_url=self.base_url,
timeout=timeout,
headers=self._headers()
)
def _headers(self) -> Dict[str, str]:
headers = {"Content-Type": "application/json"}
if self.api_key:
headers["X-API-Key"] = self.api_key
return headers
def _request(
self,
method: str,
endpoint: str,
**kwargs
) -> Dict[str, Any]:
"""Make an HTTP request."""
response = self._client.request(method, endpoint, **kwargs)
response.raise_for_status()
return response.json()
# ==================== ANALYSIS ====================
def analyze(
self,
clause_text: str,
jurisdiction: str = "INTERNATIONAL",
depth: str = "standard",
include_harmonization: bool = True,
inference_mode: str = "auto"
) -> AnalysisResult:
"""
Analyze a contract clause.
Args:
clause_text: The clause to analyze
jurisdiction: Target jurisdiction (UK, US, FRANCE, GERMANY, EU, SINGAPORE, INTERNATIONAL)
depth: Analysis depth (quick, standard, deep)
include_harmonization: Include improvement suggestions
inference_mode: LLM mode (auto, local, mistral)
Returns:
AnalysisResult with verdict and harmonization
"""
data = self._request("POST", "/v1/analyze", json={
"clause_text": clause_text,
"jurisdiction": jurisdiction,
"depth": depth,
"include_harmonization": include_harmonization,
"inference_mode": inference_mode
})
# Parse verdict
v = data.get("verdict", {})
factors = [
DecisionFactor(
rule_name=f.get("rule_name", ""),
description=f.get("rule_description", ""),
triggered=f.get("triggered", False),
impact=f.get("impact_on_risk", 0),
evidence=f.get("evidence", "")
)
for f in v.get("factors_applied", [])
]
verdict = Verdict(
risk_score=v.get("risk_score", 0),
verdict=v.get("verdict", ""),
confidence=v.get("confidence", 0.0),
factors=factors,
interpretive_gap=v.get("interpretive_gap", 0),
civilist_summary=v.get("civilist_summary", ""),
commonist_summary=v.get("commonist_summary", "")
)
# Parse harmonization
harmonization = None
h = data.get("harmonization")
if h:
harmonization = Harmonization(
golden_clause=h.get("golden_clause", ""),
rationale=h.get("rationale", ""),
risk_reduction=h.get("risk_reduction", 0)
)
return AnalysisResult(
id=data.get("id", ""),
verdict=verdict,
harmonization=harmonization,
processing_time_ms=data.get("processing_time_ms", 0)
)
def simulate(
self,
clause_text: str,
jurisdiction: str = "INTERNATIONAL",
scenario: str = None
) -> Dict[str, Any]:
"""
Run a mock trial simulation.
Args:
clause_text: The clause to simulate
jurisdiction: Target jurisdiction
scenario: Optional scenario (e.g., "pandemic", "supply_chain")
Returns:
Simulation results with transcript and outcome
"""
payload = {
"clause_text": clause_text,
"jurisdiction": jurisdiction
}
if scenario:
payload["scenario"] = scenario
return self._request("POST", "/v1/simulate", json=payload)
# ==================== CONTRACTS ====================
def list_contracts(
self,
page: int = 1,
limit: int = 20,
jurisdiction: str = None
) -> Dict[str, Any]:
"""List stored contracts."""
params = {"page": page, "limit": limit}
if jurisdiction:
params["jurisdiction"] = jurisdiction
return self._request("GET", "/v1/contracts", params=params)
def get_contract(self, contract_id: str) -> Dict[str, Any]:
"""Get a specific contract."""
return self._request("GET", f"/v1/contracts/{contract_id}")
def create_contract(
self,
name: str,
content: str,
jurisdiction: str = "INTERNATIONAL"
) -> Dict[str, Any]:
"""Create a new contract."""
return self._request("POST", "/v1/contracts", json={
"name": name,
"content": content,
"jurisdiction": jurisdiction
})
def delete_contract(self, contract_id: str) -> None:
"""Delete a contract."""
self._request("DELETE", f"/v1/contracts/{contract_id}")
# ==================== ANALYTICS ====================
def get_dashboard(self) -> Dict[str, Any]:
"""Get dashboard data."""
return self._request("GET", "/v1/analytics/dashboard")
def get_risk_trend(self, days: int = 30) -> List[Dict[str, Any]]:
"""Get risk score trend."""
return self._request("GET", f"/v1/analytics/risk-trend?days={days}")
# ==================== JOBS ====================
def bulk_analyze(
self,
contract_id: str,
clauses: List[str],
jurisdiction: str = "INTERNATIONAL"
) -> Dict[str, Any]:
"""Start a bulk analysis job."""
return self._request("POST", "/v1/jobs/bulk-analysis", json={
"contract_id": contract_id,
"clauses": clauses,
"jurisdiction": jurisdiction
})
def get_job(self, job_id: str) -> Dict[str, Any]:
"""Get job status."""
return self._request("GET", f"/v1/jobs/{job_id}")
def wait_for_job(
self,
job_id: str,
poll_interval: float = 2.0,
timeout: float = 300.0
) -> Dict[str, Any]:
"""Wait for a job to complete."""
start = time.time()
while time.time() - start < timeout:
job = self.get_job(job_id)
if job["status"] in ("completed", "failed", "cancelled"):
return job
time.sleep(poll_interval)
raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
# ==================== HEALTH ====================
def health(self) -> Dict[str, Any]:
"""Check API health."""
return self._request("GET", "/health")
def deep_health(self) -> Dict[str, Any]:
"""Deep health check with all components."""
return self._request("GET", "/health/deep")
# ==================== CLEANUP ====================
def close(self):
"""Close the HTTP client."""
self._client.close()
def __enter__(self):
return self
def __exit__(self, *args):
self.close()
# Convenience function
def analyze(
clause_text: str,
jurisdiction: str = "INTERNATIONAL",
api_key: str = None
) -> AnalysisResult:
"""
Quick analysis function.
Usage:
from bale_sdk import analyze
result = analyze("Force majeure clause...")
print(result.verdict.risk_score)
"""
with BaleClient(api_key=api_key) as client:
return client.analyze(clause_text, jurisdiction)
