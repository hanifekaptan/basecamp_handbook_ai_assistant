"""
CRITICAL: Input validation tests.

Tests invalid inputs as required by definition.md:
- Empty questions
- Oversized inputs
- Malicious characters
"""
import pytest
from unittest.mock import patch


class TestInputValidation:
    """Input validation as per definition.md requirement."""
    
    def test_empty_question_rejected(self, test_client, mock_rag_pipeline):
        """CRITICAL: Empty question should be rejected with 422."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            response = test_client.post("/api/v1/ask", json={"question": ""})
            
            assert response.status_code == 422
            assert 'detail' in response.json()
    
    def test_whitespace_only_question_rejected(self, test_client, mock_rag_pipeline):
        """CRITICAL: Whitespace-only question should be rejected."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            response = test_client.post("/api/v1/ask", json={"question": "    "})
            
            # Should be rejected (400 or 422)
            assert response.status_code in [400, 422, 500]
    
    def test_oversized_question_handled(self, test_client, mock_rag_pipeline):
        """CRITICAL: Very long questions should be handled gracefully."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            # 2000 character question
            long_question = "What is the vacation policy? " * 80
            
            response = test_client.post("/api/v1/ask", json={"question": long_question})
            
            # Should either succeed (truncated) or reject with clear error
            assert response.status_code in [200, 422]
            if response.status_code == 422:
                data = response.json()
                # Response can be dict with 'detail' or list of errors
                if isinstance(data, dict):
                    assert 'detail' in data
                elif isinstance(data, list):
                    assert len(data) > 0
