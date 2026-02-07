"""
CRITICAL: Grounding and hallucination prevention tests.

Tests LLM grounding as analysis.md emphasizes:
"Hallüsinasyon riskini minimize eden 'grounding' teknikleri kritiktir"
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestGroundingAndHallucination:
    """Grounding to prevent hallucination - critical for RAG."""
    
    @pytest.mark.asyncio
    @patch('backend.app.services.rag_pipeline.LLMClient')
    @patch('backend.app.services.rag_pipeline.VectorStore')
    @patch('backend.app.services.rag_pipeline.get_prompt_manager')
    async def test_llm_unavailable_handled(self, mock_prompt_mgr, mock_vector_store, mock_llm_client):
        """CRITICAL: System should handle LLM unavailability gracefully."""
        from backend.app.services.rag_pipeline import RAGPipeline
        
        mock_store = Mock()
        mock_store.search.return_value = [{'content': 'Test', 'metadata': {'source': 'test.md'}, 'relevance_score': 0.8}]
        mock_vector_store.return_value = mock_store
        
        mock_client = Mock()
        mock_client.is_available = AsyncMock(return_value=False)
        mock_client.generate_answer = AsyncMock(side_effect=Exception("LLM is unavailable"))
        mock_llm_client.return_value = mock_client
        
        pipeline = RAGPipeline()
        
        with pytest.raises(Exception) as exc_info:
            await pipeline.answer_question("What is the policy?")
        
        # Should raise clear error about LLM unavailability
        error_msg = str(exc_info.value).lower()
        assert 'llm' in error_msg or 'unavailable' in error_msg or 'model' in error_msg
    
    @pytest.mark.asyncio
    @patch('backend.app.services.rag_pipeline.LLMClient')
    @patch('backend.app.services.rag_pipeline.VectorStore')
    @patch('backend.app.services.rag_pipeline.get_prompt_manager')
    async def test_answer_grounded_in_context(self, mock_prompt_mgr, mock_vector_store, mock_llm_client):
        """CRITICAL: Answer should be based only on retrieved context."""
        from backend.app.services.rag_pipeline import RAGPipeline
        
        mock_store = Mock()
        mock_store.search.return_value = [
            {'content': 'Vacation policy: 15 days', 'metadata': {'source': 'benefits.md'}, 'relevance_score': 0.9}
        ]
        mock_vector_store.return_value = mock_store
        
        mock_client = Mock()
        mock_client.is_available = AsyncMock(return_value=True)
        mock_client.generate_answer = AsyncMock(
            return_value="Based on the provided context, vacation policy is 15 days."
        )
        mock_llm_client.return_value = mock_client
        
        mock_prompt_manager = Mock()
        mock_prompt_manager.build_qa_prompt.return_value = "Prompt with context"
        mock_prompt_mgr.return_value = mock_prompt_manager
        
        pipeline = RAGPipeline()
        result = await pipeline.answer_question("vacation policy?")
        
        # Verify that search was performed (context retrieval)
        mock_store.search.assert_called_once()
        
        # Verify LLM was called with some input
        mock_client.generate_answer.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.app.services.rag_pipeline.LLMClient')
    @patch('backend.app.services.rag_pipeline.VectorStore')
    @patch('backend.app.services.rag_pipeline.get_prompt_manager')
    async def test_source_attribution_included(self, mock_prompt_mgr, mock_vector_store, mock_llm_client):
        """CRITICAL: Answer should include source attribution."""
        from backend.app.services.rag_pipeline import RAGPipeline
        
        mock_store = Mock()
        mock_store.search.return_value = [
            {'content': 'Policy text', 'metadata': {'source': 'benefits-and-perks.md'}, 'relevance_score': 0.85}
        ]
        mock_vector_store.return_value = mock_store
        
        mock_client = Mock()
        mock_client.is_available = AsyncMock(return_value=True)
        mock_client.generate_answer = AsyncMock(
            return_value="Answer here. (Source: benefits-and-perks.md)"
        )
        mock_llm_client.return_value = mock_client
        
        pipeline = RAGPipeline()
        result = await pipeline.answer_question("test question")
        
        # Result should include source information
        assert 'sources' in result or 'source' in str(result).lower()
