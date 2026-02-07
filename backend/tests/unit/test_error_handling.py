"""
CRITICAL: Error handling test.

Tests exception handling as required by definition.md:
"beklenmeyen bir giriş geldiğinde bunları yakalayıp uygun hata mesajları"
"""
import pytest
from unittest.mock import Mock, patch


class TestErrorHandling:
    """Error handling and graceful degradation."""
    
    def test_api_error_handling_with_proper_messages(self, test_client, mock_rag_pipeline):
        """CRITICAL: Errors should return clear, user-friendly messages."""
        with patch('backend.app.api.endpoints.ask.get_rag_pipeline', return_value=mock_rag_pipeline):
            # Simulate pipeline error
            mock_rag_pipeline.answer_question.side_effect = Exception("Database connection failed")
            
            response = test_client.post(
                "/api/v1/ask",
                json={"question": "What is the vacation policy?"}
            )
            
            # Should return 500 with error message
            assert response.status_code == 500
            data = response.json()
            
            # Error message should be informative
            assert 'detail' in data
            assert len(data['detail']) > 10  # Not just "Error"
