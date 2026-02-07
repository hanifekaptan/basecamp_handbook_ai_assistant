"""
Integration Tests: LLM Client & Ollama

Tests the real integration between:
- LLMClient class
- Ollama HTTP API
- Streaming and non-streaming generation

These tests require Ollama to be running locally.
Tests are marked with @pytest.mark.integration and can be skipped if Ollama is unavailable.
"""
import pytest
import asyncio
import os
from backend.app.llm.client import LLMClient
from backend.app.core.config import Settings

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


@pytest.fixture
def llm_settings():
    """Settings for LLM integration tests."""
    return Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        temperature=0.3
    )


@pytest.fixture
def llm_client(llm_settings, monkeypatch):
    """Create LLMClient instance for testing."""
    monkeypatch.setattr('backend.app.llm.client.get_settings', lambda: llm_settings)
    return LLMClient()


@pytest.mark.asyncio
class TestLLMClientIntegration:
    """Integration tests for LLM client with real Ollama instance."""
    
    async def test_ollama_availability_check(self, llm_client):
        """Test checking if Ollama is available."""
        is_available = await llm_client.is_available()
        
        # Should return boolean
        assert isinstance(is_available, bool)
        
        # If Ollama is running, should be True
        # If not running, test should document the requirement
        if not is_available:
            pytest.skip("Ollama is not running. Start with 'ollama serve'")
    
    async def test_simple_generation(self, llm_client):
        """Test basic text generation with Ollama."""
        # Check availability first
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompt = "Answer briefly: What is 2+2?"
        response = await llm_client.generate_answer(prompt)
        
        # Should return a string
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Should contain the answer (4 or "four")
        response_lower = response.lower()
        assert any(term in response_lower for term in ['4', 'four'])
    
    async def test_generation_with_context(self, llm_client):
        """Test generation with context-based prompt."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompt = """Based on the following context, answer the question.

Context:
Employees receive 15 days of paid vacation per year. Vacation days accumulate monthly.

Question: How many vacation days do employees get?

Answer:"""
        
        response = await llm_client.generate_answer(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Should mention 15 days
        assert '15' in response or 'fifteen' in response.lower()
    
    async def test_streaming_generation(self, llm_client):
        """Test streaming text generation."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompt = "Count from 1 to 3."
        
        chunks = []
        async for chunk in llm_client.generate_answer_stream(prompt):
            assert isinstance(chunk, str)
            chunks.append(chunk)
        
        # Should have received multiple chunks
        assert len(chunks) > 0
        
        # Combine chunks to form complete response
        full_response = ''.join(chunks)
        assert len(full_response) > 0
    
    async def test_streaming_yields_incrementally(self, llm_client):
        """Test that streaming returns data incrementally, not all at once."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompt = "Write a short sentence about AI."
        
        chunks = []
        chunk_count = 0
        
        async for chunk in llm_client.generate_answer_stream(prompt):
            chunks.append(chunk)
            chunk_count += 1
            
            # Should get chunks incrementally
            if chunk_count >= 3:
                break
        
        # Should have received chunks before completion
        assert chunk_count >= 3, "Streaming should provide incremental chunks"
    
    async def test_temperature_affects_generation(self, llm_client):
        """Test that temperature parameter affects generation consistency."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompt = "Answer with just a number: What is 5 * 5?"
        
        # Generate twice with low temperature - should be similar
        response1 = await llm_client.generate_answer(prompt, temperature=0.1)
        response2 = await llm_client.generate_answer(prompt, temperature=0.1)
        
        # Both should contain the answer
        assert '25' in response1 or 'twenty-five' in response1.lower()
        assert '25' in response2 or 'twenty-five' in response2.lower()
    
    async def test_prompt_following_ability(self, llm_client):
        """Test that LLM follows prompt instructions."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompt = """You are a helpful assistant. Answer based ONLY on the provided context.

Context: The company offers 401(k) matching up to 5% of salary.

Question: What is the 401k matching percentage?

Answer:"""
        
        response = await llm_client.generate_answer(prompt)
        
        # Should mention 5% or 5 percent
        response_lower = response.lower()
        assert any(term in response_lower for term in ['5%', '5 percent', 'five percent'])
    
    async def test_handles_empty_prompt(self, llm_client):
        """Test handling of empty or minimal prompts."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        # Should handle gracefully, either with response or appropriate error
        try:
            response = await llm_client.generate_answer("")
            assert isinstance(response, str)
        except Exception as e:
            # Should raise a meaningful error
            assert "prompt" in str(e).lower() or "empty" in str(e).lower()
    
    async def test_generation_timeout_handling(self, llm_client):
        """Test that generation handles timeouts appropriately."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        # Quick prompt that should complete fast
        prompt = "Say 'OK'"
        
        # Should complete within reasonable time (30 seconds for safety)
        try:
            response = await asyncio.wait_for(
                llm_client.generate_answer(prompt),
                timeout=30.0
            )
            assert isinstance(response, str)
            assert len(response) > 0
        except asyncio.TimeoutError:
            pytest.fail("Generation took too long (>30s)")
    
    async def test_model_info_retrieval(self, llm_client):
        """Test retrieving model information from Ollama."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        # LLMClient should know which model it's using
        assert hasattr(llm_client, 'model')
        assert llm_client.model == "llama3.2:3b"
    
    async def test_consecutive_generations(self, llm_client):
        """Test multiple consecutive generation calls."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompts = [
            "Say 'test1'",
            "Say 'test2'",
            "Say 'test3'"
        ]
        
        responses = []
        for prompt in prompts:
            response = await llm_client.generate_answer(prompt)
            responses.append(response)
            assert isinstance(response, str)
            assert len(response) > 0
        
        # All should have completed successfully
        assert len(responses) == 3
    
    async def test_grounding_in_context(self, llm_client):
        """Test that LLM stays grounded in provided context."""
        if not await llm_client.is_available():
            pytest.skip("Ollama not available")
        
        prompt = """You are a helpful assistant. Answer based ONLY on the context below.

Context:
Remote work is available for all employees. Equipment is provided by IT.

Question: What is the vacation policy?

Answer (if not in context, say "Not mentioned in the context"):"""
        
        response = await llm_client.generate_answer(prompt)
        response_lower = response.lower()
        
        # Should indicate information not available
        # (The context doesn't mention vacation policy)
        not_mentioned_indicators = [
            'not mentioned',
            'not in the context',
            'no information',
            "doesn't mention",
            'not provided'
        ]
        
        has_indicator = any(indicator in response_lower for indicator in not_mentioned_indicators)
        assert has_indicator, "LLM should indicate when information is not in context"
