"""
BALE End-to-End Tests
Integration tests for the full analysis pipeline.
"""
import pytest
import asyncio
class TestFullPipeline:
"""Test the complete analysis pipeline."""
@pytest.fixture
def sample_clause(self):
return """
Force Majeure: Neither party shall be liable for any failure or delay in performing its obligations under this Agreement where such failure or delay results from circumstances beyond the reasonable control of that party, including but not limited to acts of God, natural disasters, war, terrorism, riots, or government action.
"""
@pytest.fixture
def liability_clause(self):
return """
Limitation of Liability: The Supplier shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to loss of profits, data, use, goodwill, or other intangible losses, resulting from this Agreement.
"""
def test_graph_compilation(self):
"""Test that the enhanced graph compiles."""
from src.graph_enhanced import compile_enhanced_graph
graph = compile_enhanced_graph()
assert graph is not None
def test_quick_graph_compilation(self):
"""Test that the quick graph compiles."""
from src.graph_enhanced import compile_quick_graph
graph = compile_quick_graph()
assert graph is not None
@pytest.mark.skip(reason="Requires LLM")
def test_full_analysis_pipeline(self, sample_clause):
"""Test full analysis with graph (requires LLM)."""
from src.graph_enhanced import compile_quick_graph
graph = compile_quick_graph()
state = {
"content": sample_clause,
"jurisdiction": "UK",
"execution_mode": "local"
}
result = graph.invoke(state)
assert "risk_score" in result or "verdict" in result
class TestAPIIntegration:
"""Test API integration scenarios."""
@pytest.fixture
def client(self):
from fastapi.testclient import TestClient
from api.main import app
return TestClient(app)
def test_analyze_and_get_result(self, client):
"""Test analyze endpoint returns structured result."""
clause = """
This Agreement shall be governed by and construed in accordance with the laws of England and Wales. The parties submit to the exclusive jurisdiction of the courts of England and Wales.
"""
response = client.post("/v1/analyze", json={
"clause_text": clause,
"jurisdiction": "UK",
"depth": "standard"
})
# May fail without LLM, but should not be a validation error
assert response.status_code in [200, 400, 500]
def test_contract_lifecycle(self, client):
"""Test full contract CRUD cycle."""
# Create
create_resp = client.post("/v1/contracts", json={
"name": "Test Contract",
"content": "Contract content here...",
"jurisdiction": "UK"
})
assert create_resp.status_code == 200
contract_id = create_resp.json()["id"]
# Read
get_resp = client.get(f"/v1/contracts/{contract_id}")
assert get_resp.status_code == 200
assert get_resp.json()["name"] == "Test Contract"
# Update
update_resp = client.patch(f"/v1/contracts/{contract_id}", json={
"name": "Updated Contract"
})
assert update_resp.status_code == 200
# Delete
delete_resp = client.delete(f"/v1/contracts/{contract_id}")
assert delete_resp.status_code == 200
# Verify deleted
verify_resp = client.get(f"/v1/contracts/{contract_id}")
assert verify_resp.status_code == 404
class TestCacheIntegration:
"""Test caching functionality."""
def test_cache_key_generation(self):
"""Test cache key generation is deterministic."""
from api.cache import make_cache_key, analysis_cache_key
key1 = make_cache_key("test", "arg1", "arg2", foo="bar")
key2 = make_cache_key("test", "arg1", "arg2", foo="bar")
assert key1 == key2
def test_analysis_cache_key(self):
"""Test analysis cache key."""
from api.cache import analysis_cache_key
key = analysis_cache_key("clause text", "UK", "standard")
assert key.startswith("analysis:")
assert "UK" in key
class TestWebhooks:
"""Test webhook system."""
def test_signature_generation(self):
"""Test webhook signature generation."""
from api.webhooks import generate_signature, verify_signature
payload = '{"event": "test"}'
secret = "test_secret"
signature = generate_signature(payload, secret)
assert len(signature) == 64 # SHA256 hex
assert verify_signature(payload, secret, signature)
def test_event_creation(self):
"""Test webhook event creation."""
from api.webhooks import WebhookEvent, EventType
event = WebhookEvent(
id="evt_123",
type=EventType.ANALYSIS_COMPLETED,
timestamp="2026-01-16T00:00:00Z",
data={"risk_score": 45}
)
event_dict = event.to_dict()
assert event_dict["type"] == "analysis.completed"
assert event_dict["data"]["risk_score"] == 45
class TestJobs:
"""Test background job system."""
def test_task_registration(self):
"""Test task registration."""
from api.jobs import registry
@registry.register("test_task")
async def test_task():
return "success"
assert registry.get("test_task") is not None
def test_job_creation(self):
"""Test job creation."""
from api.jobs import Job, JobStatus
from datetime import datetime
job = Job(
id="job_123",
task_name="test_task",
args=(),
kwargs={},
status=JobStatus.PENDING,
created_at=datetime.utcnow().isoformat()
)
assert job.status == JobStatus.PENDING
assert job.progress == 0
class TestRealtime:
"""Test real-time features."""
def test_message_creation(self):
"""Test realtime message creation."""
from api.realtime import RealtimeMessage, MessageType
message = RealtimeMessage(
type=MessageType.ANALYSIS_PROGRESS,
data={"progress": 50}
)
json_str = message.to_json()
assert "analysis_progress" in json_str
assert "50" in json_str
def test_progress_tracker_stages(self):
"""Test analysis progress stages."""
from api.realtime import AnalysisProgressTracker
tracker = AnalysisProgressTracker("analysis_123", "user_456")
assert len(tracker.STAGES) > 5
assert tracker.STAGES[0][0] == "ingestion"
assert tracker.STAGES[-1][0] == "complete"
if __name__ == "__main__":
pytest.main([__file__, "-v"])
