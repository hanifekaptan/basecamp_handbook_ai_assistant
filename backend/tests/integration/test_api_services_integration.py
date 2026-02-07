"""
Integration Tests: API Endpoints with Real Services

Tests API endpoints using real backend services:
- FastAPI endpoints
- Real RAG pipeline
- Real vector store
- Real LLM client (Ollama)

These tests verify the complete system integration from HTTP request to response.
Requires Ollama to be running.
"""
import pytest
import tempfile
import shutil
import os
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.core.config import Settings
import json

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


@pytest.fixture
def api_test_docs_dir():
    """Create test documents for API integration tests."""
    temp_dir = tempfile.mkdtemp()
    docs_path = Path(temp_dir)
    
    (docs_path / "company-policies.md").write_text("""
# Company Policies

## Work Hours
Flexible working hours. Work when you're most productive.
Aim for 4 hours overlap with your team.

## Communication
Use Slack for urgent matters, Basecamp for everything else.
Response time expectation: 1 business day.

## Time Off
Unlimited vacation policy. Just coordinate with your team.
We encourage taking at least 3 weeks per year.
    """)
    
    yield docs_path
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def api_integration_settings(api_test_docs_dir):
    """Settings for API integration tests."""
    temp_chroma = tempfile.mkdtemp()
    
    settings = Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        chroma_persist_directory=temp_chroma,
        chroma_collection_name="api_integration_test",
        docs_directory=str(api_test_docs_dir),
        chunk_size=512,
        chunk_overlap=50,
        top_k_results=3
    )
    
    yield settings
    
    # Cleanup
    shutil.rmtree(temp_chroma, ignore_errors=True)


@pytest.fixture
def api_test_client(api_integration_settings, monkeypatch):
    """Create test client with real services."""
    # Patch all get_settings calls throughout the app
    monkeypatch.setattr('backend.app.core.config.get_settings', lambda: api_integration_settings)
    monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: api_integration_settings)
    monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: api_integration_settings)
    monkeypatch.setattr('backend.app.llm.client.get_settings', lambda: api_integration_settings)
    monkeypatch.setattr('backend.app.services.rag_pipeline.get_settings', lambda: api_integration_settings)
    monkeypatch.setattr('backend.main.get_settings', lambda: api_integration_settings)
    
    # Import after patching
    from backend.main import create_application
    app = create_application()
    
    # Initialize vector store
    from backend.app.api.dependencies import get_rag_pipeline
    pipeline = get_rag_pipeline()
    pipeline.vector_store.index_documents(str(api_integration_settings.docs_directory))
    
    return TestClient(app)


class TestAPIServicesIntegration:
    """Integration tests for API endpoints with real services."""
    
    def test_health_endpoint_with_real_services(self, api_test_client):
        """Test /health endpoint checks real service availability."""
        response = api_test_client.get("/api/v1/health")
        
        # Should always respond
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert 'status' in data
        assert 'ollama_available' in data
        assert 'documents_indexed' in data
        
        # If Ollama is running, should report healthy
        if data['ollama_available']:
            assert data['status'] in ['healthy', 'degraded']
        
        # Should have indexed our test document
        if response.status_code == 200:
            assert data['documents_indexed'] > 0
    
    def test_ask_endpoint_complete_workflow(self, api_test_client):
        """Test /ask endpoint with complete RAG workflow."""
        # Skip if Ollama not available
        health = api_test_client.get("/api/v1/health")
        if not health.json().get('ollama_available'):
            pytest.skip("Ollama not available")
        
        response = api_test_client.post(
            "/api/v1/ask",
            json={"question": "What is the vacation policy?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'answer' in data
        assert 'sources' in data
        assert 'question' in data
        assert 'metadata' in data
        
        # Verify answer quality
        assert len(data['answer']) > 10
        answer_lower = data['answer'].lower()
        assert 'unlimited' in answer_lower or 'vacation' in answer_lower
        
        # Verify sources
        assert len(data['sources']) > 0
        for source in data['sources']:
            assert 'content' in source
            assert 'source' in source
            assert 'relevance_score' in source
    
    def test_ask_endpoint_input_validation(self, api_test_client):
        """Test input validation on /ask endpoint."""
        # Empty question
        response = api_test_client.post(
            "/api/v1/ask",
            json={"question": ""}
        )
        assert response.status_code == 422
        
        # Missing question
        response = api_test_client.post(
            "/api/v1/ask",
            json={}
        )
        assert response.status_code == 422
        
        # Question too long (>1000 chars)
        response = api_test_client.post(
            "/api/v1/ask",
            json={"question": "x" * 1001}
        )
        assert response.status_code == 422
    
    def test_ask_stream_endpoint(self, api_test_client):
        """Test /ask/stream endpoint with real streaming."""
        # Skip if Ollama not available
        health = api_test_client.get("/api/v1/health")
        if not health.json().get('ollama_available'):
            pytest.skip("Ollama not available")
        
        # TestClient doesn't support streaming well, but we can test it responds
        response = api_test_client.post(
            "/api/v1/ask/stream",
            json={"question": "What are the work hours?"}
        )
        
        # Should start streaming (200) or Ollama not available (503)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            # Content should be text/event-stream
            assert 'text/event-stream' in response.headers.get('content-type', '')
            
            # Should have content
            assert len(response.content) > 0
    
    def test_metrics_performance_endpoint(self, api_test_client):
        """Test /metrics/performance endpoint."""
        response = api_test_client.get("/api/v1/metrics/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have performance metrics
        assert 'cpu_percent' in data
        assert 'memory_percent' in data
        assert 'disk_percent' in data
        
        # Values should be reasonable
        assert 0 <= data['cpu_percent'] <= 100
        assert 0 <= data['memory_percent'] <= 100
        assert 0 <= data['disk_percent'] <= 100
    
    def test_metrics_usage_endpoint(self, api_test_client):
        """Test /metrics/usage endpoint."""
        response = api_test_client.get("/api/v1/metrics/usage")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have usage metrics
        assert 'vector_db' in data
        assert 'llm' in data
        
        # Vector DB metrics
        vdb = data['vector_db']
        assert 'total_documents' in vdb
        assert 'collection_name' in vdb
        
        # LLM metrics
        llm = data['llm']
        assert 'model' in llm
        assert 'base_url' in llm
    
    def test_metrics_system_endpoint(self, api_test_client):
        """Test /metrics/system endpoint."""
        response = api_test_client.get("/api/v1/metrics/system")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have system health metrics
        assert 'health_score' in data
        assert 'status' in data
        assert 'components' in data
        
        # Health score should be 0-100
        assert 0 <= data['health_score'] <= 100
        
        # Components status
        components = data['components']
        assert 'ollama' in components
        assert 'vector_db' in components
    
    def test_rate_limiting(self, api_test_client):
        """Test that rate limiting is enforced."""
        # Skip if Ollama not available
        health = api_test_client.get("/api/v1/health")
        if not health.json().get('ollama_available'):
            pytest.skip("Ollama not available")
        
        # Make many rapid requests (rate limit is 20/min)
        responses = []
        for i in range(25):
            response = api_test_client.post(
                "/api/v1/ask",
                json={"question": f"Test question {i}"}
            )
            responses.append(response.status_code)
        
        # Should eventually hit rate limit (429)
        assert 429 in responses, "Rate limiting not enforced"
    
    def test_error_handling_ollama_down(self, api_test_client, monkeypatch):
        """Test error handling when Ollama is unavailable."""
        # This test would need to mock Ollama being down
        # For now, just verify health endpoint reports status
        response = api_test_client.get("/api/v1/health")
        
        data = response.json()
        assert 'ollama_available' in data
        
        # If Ollama is down, status should reflect it
        if not data['ollama_available']:
            assert data['status'] in ['degraded', 'unhealthy']
            assert response.status_code == 503
    
    def test_concurrent_requests(self, api_test_client):
        """Test handling multiple concurrent requests."""
        # Skip if Ollama not available
        health = api_test_client.get("/api/v1/health")
        if not health.json().get('ollama_available'):
            pytest.skip("Ollama not available")
        
        import concurrent.futures
        
        def make_request(question):
            return api_test_client.post(
                "/api/v1/ask",
                json={"question": question}
            )
        
        questions = [
            "What is the vacation policy?",
            "What are the work hours?",
            "How does communication work?"
        ]
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, q) for q in questions]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed (or hit rate limit)
        for response in responses:
            assert response.status_code in [200, 429]
        
        # At least one should succeed
        assert any(r.status_code == 200 for r in responses)
    
    def test_api_response_timing(self, api_test_client):
        """Test that API responses complete within reasonable time."""
        # Skip if Ollama not available
        health = api_test_client.get("/api/v1/health")
        if not health.json().get('ollama_available'):
            pytest.skip("Ollama not available")
        
        import time
        
        start = time.time()
        response = api_test_client.post(
            "/api/v1/ask",
            json={"question": "What is the vacation policy?"}
        )
        duration = time.time() - start
        
        # Should complete within reasonable time (30 seconds max)
        assert duration < 30, f"Request took too long: {duration}s"
        
        # Should be successful
        if response.status_code == 200:
            assert 'answer' in response.json()
    
    def test_api_documentation_accessible(self, api_test_client):
        """Test that API documentation endpoints are accessible."""
        # OpenAPI docs
        response = api_test_client.get("/docs")
        assert response.status_code == 200
        
        # OpenAPI schema
        response = api_test_client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert 'openapi' in schema
        assert 'paths' in schema
        
        # Should have our key endpoints
        paths = schema['paths']
        assert '/api/v1/health' in paths
        assert '/api/v1/ask' in paths
        assert '/api/v1/ask/stream' in paths
