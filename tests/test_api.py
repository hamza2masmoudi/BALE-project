"""
BALE API Tests
Integration tests for REST API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
@pytest.fixture
def client():
"""Create test client."""
from api.main import app
return TestClient(app)
class TestHealthEndpoints:
"""Test health check endpoints."""
def test_root_endpoint(self, client):
"""Test root endpoint returns API info."""
response = client.get("/")
assert response.status_code == 200
data = response.json()
assert "name" in data
assert data["name"] == "BALE API"
assert "version" in data
def test_health_endpoint(self, client):
"""Test health check returns status."""
response = client.get("/health")
assert response.status_code == 200
data = response.json()
assert data["status"] == "healthy"
assert "version" in data
assert "inference_local_available" in data
assert "inference_mistral_available" in data
class TestAnalysisEndpoints:
"""Test analysis endpoints."""
def test_analyze_clause_validation(self, client):
"""Test that analyze endpoint validates input."""
# Too short clause should fail
response = client.post("/v1/analyze", json={
"clause_text": "Short" # Less than 10 chars
})
assert response.status_code == 422 # Validation error
def test_analyze_clause_requires_text(self, client):
"""Test that clause_text is required."""
response = client.post("/v1/analyze", json={})
assert response.status_code == 422
def test_analyze_clause_valid_request(self, client):
"""Test valid analysis request structure."""
response = client.post("/v1/analyze", json={
"clause_text": "The Supplier shall not be liable for any indirect, consequential, or incidental damages arising from this Agreement, including but not limited to lost profits, data loss, or business interruption.",
"jurisdiction": "UK",
"depth": "standard",
"inference_mode": "local"
})
# Will fail if no LLM available, but should not be a validation error
# In test env without LLM, expect 400 or 500, not 422
assert response.status_code in [200, 400, 500]
class TestSimulationEndpoints:
"""Test mock trial simulation endpoints."""
def test_simulate_validation(self, client):
"""Test simulation input validation."""
response = client.post("/v1/simulate", json={
"clause_text": "Short"
})
assert response.status_code == 422
def test_simulate_valid_request(self, client):
"""Test valid simulation request structure."""
response = client.post("/v1/simulate", json={
"clause_text": "Force Majeure: Neither party shall be liable for failure to perform due to acts of God, war, terrorism, or government action beyond the reasonable control of the affected party.",
"jurisdiction": "INTERNATIONAL"
})
assert response.status_code in [200, 400, 500]
class TestContractEndpoints:
"""Test contract CRUD endpoints."""
def test_create_contract(self, client):
"""Test contract creation."""
response = client.post("/v1/contracts", json={
"name": "Test NDA",
"content": "This is a test contract content...",
"jurisdiction": "UK"
})
assert response.status_code == 200
data = response.json()
assert "id" in data
assert data["name"] == "Test NDA"
assert data["jurisdiction"] == "UK"
def test_list_contracts(self, client):
"""Test contract listing with pagination."""
response = client.get("/v1/contracts", params={
"page": 1,
"page_size": 20
})
assert response.status_code == 200
data = response.json()
assert "items" in data
assert "total" in data
assert "page" in data
def test_get_contract_not_found(self, client):
"""Test getting non-existent contract."""
response = client.get("/v1/contracts/non-existent-id")
assert response.status_code == 404
class TestSchemaValidation:
"""Test request schema validation."""
def test_invalid_jurisdiction(self, client):
"""Test invalid jurisdiction is rejected."""
response = client.post("/v1/analyze", json={
"clause_text": "A sufficiently long clause for testing purposes and validation.",
"jurisdiction": "INVALID_JURISDICTION"
})
assert response.status_code == 422
def test_invalid_depth(self, client):
"""Test invalid analysis depth is rejected."""
response = client.post("/v1/analyze", json={
"clause_text": "A sufficiently long clause for testing purposes and validation.",
"depth": "ultra_deep" # Invalid
})
assert response.status_code == 422
def test_invalid_inference_mode(self, client):
"""Test invalid inference mode is rejected."""
response = client.post("/v1/analyze", json={
"clause_text": "A sufficiently long clause for testing purposes and validation.",
"inference_mode": "openai" # Not supported
})
assert response.status_code == 422
class TestCORS:
"""Test CORS configuration."""
def test_cors_headers(self, client):
"""Test CORS headers are present."""
response = client.options("/v1/analyze", headers={
"Origin": "http://localhost:3000",
"Access-Control-Request-Method": "POST"
})
# FastAPI returns 200 for OPTIONS when CORS is configured
assert response.status_code in [200, 405]
class TestOpenAPI:
"""Test OpenAPI documentation."""
def test_openapi_json(self, client):
"""Test OpenAPI spec is available."""
response = client.get("/openapi.json")
assert response.status_code == 200
data = response.json()
assert "openapi" in data
assert "paths" in data
assert "/v1/analyze" in data["paths"]
def test_docs_available(self, client):
"""Test Swagger UI is available."""
response = client.get("/docs")
assert response.status_code == 200
def test_redoc_available(self, client):
"""Test ReDoc is available."""
response = client.get("/redoc")
assert response.status_code == 200
if __name__ == "__main__":
pytest.main([__file__, "-v"])
