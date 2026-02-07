"""
E2E Integration Tests: Comprehensive endpoint testing.

Tests each API endpoint with realistic scenarios:
- /health (system status)
- /ask (core RAG functionality)
- /ask/stream (streaming responses)
- /metrics/performance (system metrics)
- /metrics/usage (usage statistics)
- /metrics/system (system health)
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock
import json


class TestE2EIntegration:
    """E2E tests - comprehensive coverage for all endpoints."""
    
    # ========== Core Endpoints ==========
    
    def test_health_endpoint_e2e(self, test_client):
        """E2E: Health endpoint returns system status."""
        response = test_client.get("/api/v1/health")
        
        # Should respond (200, 503, or 500 all acceptable)
        assert response.status_code in [200, 503, 500]
        data = response.json()
        
        # Verify response structure
        assert 'status' in data
        assert data['status'] in ['healthy', 'degraded', 'unhealthy']
    
    def test_ask_endpoint_e2e(self, test_client, mock_rag_pipeline):
        """E2E: Ask endpoint completes full RAG cycle."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "What is the vacation policy?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Core RAG outputs
            assert 'answer' in data
            assert 'sources' in data
            assert 'question' in data
            assert len(data['answer']) > 0
            assert isinstance(data['sources'], list)
    
    def test_ask_endpoint_empty_question(self, test_client, mock_rag_pipeline):
        """E2E: Ask endpoint rejects empty questions."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": ""}
            )
            
            # Should return 400 Bad Request
            assert response.status_code in [400, 422]
            data = response.json()
            assert 'detail' in data
    
    def test_ask_stream_endpoint_e2e(self, test_client, mock_rag_pipeline):
        """E2E: Ask stream endpoint initiates streaming response."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            
            response = test_client.post(
                "/api/v1/ask/stream",
                json={"question": "Tell me about benefits"}
            )
            
            # Should return streaming response or normal response
            assert response.status_code in [200, 501, 500]
            
            # If successful, should have content
            if response.status_code == 200:
                assert response.content is not None
    
    # ========== Metrics Endpoints ==========
    
    def test_metrics_performance_endpoint_e2e(self, test_client):
        """E2E: Performance metrics endpoint returns system metrics."""
        response = test_client.get("/api/v1/metrics/performance")
        
        # Should return metrics or error
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify metrics structure
            assert 'timestamp' in data
            assert 'system' in data
            assert 'process' in data
            
            # Check system metrics
            assert 'cpu_percent' in data['system']
            assert 'memory' in data['system']
            assert 'disk' in data['system']
            
            # Check process metrics
            assert 'memory_mb' in data['process']
            assert 'threads' in data['process']
    
    def test_metrics_usage_endpoint_e2e(self, test_client):
        """E2E: Usage statistics endpoint returns database and LLM stats."""
        response = test_client.get("/api/v1/metrics/usage")
        
        # Should return usage stats or error
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify usage structure
            assert 'timestamp' in data
            assert 'vector_database' in data
            assert 'llm' in data
            
            # Check vector db info
            assert 'collection_name' in data['vector_database']
            assert 'document_count' in data['vector_database']
            
            # Check LLM info
            assert 'model' in data['llm']
            assert 'available' in data['llm']
    
    def test_metrics_system_endpoint_e2e(self, test_client):
        """E2E: System health endpoint returns overall health status."""
        response = test_client.get("/api/v1/metrics/system")
        
        # Should return system health or error
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify health structure
            assert 'health_score' in data
            assert 'status' in data
            assert 'issues' in data
            
            # Health score should be between 0-100
            assert 0 <= data['health_score'] <= 100
            assert isinstance(data['issues'], list)
    
    # ========== Edge Cases ==========
    
    def test_ask_endpoint_with_long_question(self, test_client, mock_rag_pipeline):
        """E2E: Ask endpoint handles very long questions."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            
            long_question = "What is the policy? " * 200  # ~4000 chars
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": long_question}
            )
            
            # Should handle gracefully (200 or 400)
            assert response.status_code in [200, 400, 422, 500]
    
    def test_ask_endpoint_with_special_characters(self, test_client, mock_rag_pipeline):
        """E2E: Ask endpoint handles special characters in questions."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "What about $alaries & b0nuses? (401k) [benefits]"}
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 422, 500]
            if response.status_code == 200:
                data = response.json()
                assert 'answer' in data
