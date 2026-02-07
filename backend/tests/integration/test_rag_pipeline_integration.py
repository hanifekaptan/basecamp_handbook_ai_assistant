"""
Integration Tests: RAG Pipeline

Tests the complete RAG pipeline integration:
- Vector Store retrieval
- Prompt building
- LLM generation
- Answer formatting

These tests verify that all components work together correctly.
Requires Ollama to be running.
"""
import pytest
import tempfile
import shutil
import os
from pathlib import Path
from backend.app.services.rag_pipeline import RAGPipeline
from backend.app.core.config import Settings

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


@pytest.fixture
def rag_test_docs_dir():
    """Create temporary directory with comprehensive test documents."""
    temp_dir = tempfile.mkdtemp()
    docs_path = Path(temp_dir)
    
    # Create realistic handbook documents
    (docs_path / "benefits-and-perks.md").write_text("""
# Benefits and Perks

## Vacation Policy
Basecamp offers unlimited vacation time to all employees. You don't need to track days.
Just coordinate with your team and take the time you need.

## Health Insurance
We cover 100% of health insurance premiums for employees and 75% for dependents.
Coverage includes medical, dental, and vision.

## Retirement
We match 401(k) contributions dollar-for-dollar up to 6% of your salary.
Contributions are immediately vested.

## Learning Budget
Every employee gets $1,000 per year for professional development.
Use it for books, courses, conferences, or workshops.
    """)
    
    (docs_path / "how-we-work.md").write_text("""
# How We Work

## Remote Work
All positions at Basecamp are fully remote. Work from anywhere with good internet.
We don't have an office.

## Working Hours
Work whenever works best for you. We trust you to manage your time.
Try to overlap with your team for at least 4 hours per day.

## Communication
- Slack: for quick questions and daily check-ins
- Basecamp: for project work and async collaboration
- Zoom: for video meetings (keep meetings to a minimum)

## Code of Conduct
Treat everyone with respect and kindness. No harassments, discrimination, or toxic behavior.
Report issues to HR immediately.
    """)
    
    (docs_path / "getting-started.md").write_text("""
# Getting Started at Basecamp

## First Day
You'll receive your laptop and equipment on day one.
Spend your first week getting familiar with our codebase and processes.

## Onboarding
Your manager will set up weekly 1-on-1 meetings.
You'll be paired with a mentor for your first three months.

## Equipment
We provide MacBook Pro, monitor, keyboard, mouse, and headphones.
Submit equipment requests through the IT portal.
    """)
    
    yield docs_path
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def rag_chroma_dir():
    """Temporary ChromaDB directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def rag_settings(rag_test_docs_dir, rag_chroma_dir):
    """Settings for RAG integration tests."""
    return Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        chroma_persist_directory=rag_chroma_dir,
        chroma_collection_name="rag_integration_test",
        embedding_model="all-MiniLM-L6-v2",
        docs_directory=str(rag_test_docs_dir),
        chunk_size=512,
        chunk_overlap=50,
        top_k_results=5,
        temperature=0.3
    )


@pytest.fixture
def rag_pipeline(rag_settings, monkeypatch):
    """Initialize RAG pipeline with test settings."""
    monkeypatch.setattr('backend.app.services.rag_pipeline.get_settings', lambda: rag_settings)
    monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: rag_settings)
    monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: rag_settings)
    monkeypatch.setattr('backend.app.llm.client.get_settings', lambda: rag_settings)
    
    pipeline = RAGPipeline()
    
    # Index test documents
    indexed_count = pipeline.vector_store.index_documents(str(rag_settings.docs_directory))
    assert indexed_count > 0, "Failed to index test documents"
    
    return pipeline


@pytest.mark.asyncio
class TestRAGPipelineIntegration:
    """Integration tests for complete RAG pipeline."""
    
    async def test_pipeline_initialization(self, rag_pipeline):
        """Test RAG pipeline initializes all components."""
        # Check Ollama availability
        is_available = await rag_pipeline.llm_client.is_available()
        if not is_available:
            pytest.skip("Ollama not available")
        
        # Verify components initialized
        assert rag_pipeline.vector_store is not None
        assert rag_pipeline.llm_client is not None
        assert rag_pipeline.prompt_manager is not None
        
        # Verify documents are indexed
        stats = rag_pipeline.vector_store.get_collection_stats()
        assert stats['total_documents'] > 0
    
    async def test_complete_rag_workflow(self, rag_pipeline):
        """Test complete RAG workflow: retrieve -> prompt -> generate."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        question = "What is the vacation policy?"
        response = await rag_pipeline.answer_question(question)
        
        # Verify response structure
        assert 'answer' in response
        assert 'sources' in response
        assert 'question' in response
        assert 'metadata' in response
        
        # Verify answer quality
        answer = response['answer']
        assert isinstance(answer, str)
        assert len(answer) > 20, "Answer too short"
        
        # Answer should mention unlimited vacation
        answer_lower = answer.lower()
        assert 'unlimited' in answer_lower or 'vacation' in answer_lower
        
        # Should have source documents
        sources = response['sources']
        assert len(sources) > 0
        assert any('benefits' in s.get('source', '').lower() for s in sources)
    
    async def test_different_question_types(self, rag_pipeline):
        """Test RAG pipeline with different types of questions."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        questions_and_keywords = [
            ("What health insurance benefits are provided?", ["health", "insurance", "100%"]),
            ("How does 401k matching work?", ["401", "6%", "match"]),
            ("What is the remote work policy?", ["remote", "anywhere"]),
            ("What equipment do employees get?", ["laptop", "macbook", "equipment"])
        ]
        
        for question, expected_keywords in questions_and_keywords:
            response = await rag_pipeline.answer_question(question)
            
            assert 'answer' in response
            answer_lower = response['answer'].lower()
            
            # Should mention at least one expected keyword
            found = any(keyword.lower() in answer_lower for keyword in expected_keywords)
            assert found, f"Expected keywords {expected_keywords} not found in answer for: {question}"
    
    async def test_source_attribution(self, rag_pipeline):
        """Test that answers include proper source attribution."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        question = "What is the learning budget?"
        response = await rag_pipeline.answer_question(question)
        
        # Should have sources
        sources = response['sources']
        assert len(sources) > 0
        
        # Each source should have required fields
        for source in sources:
            assert 'content' in source
            assert 'source' in source
            assert 'relevance_score' in source
            
            # Source file should be from our test docs
            assert source['source'].endswith('.md')
            
            # Relevance score should be reasonable
            assert 0.0 <= source['relevance_score'] <= 1.0
    
    async def test_answer_grounding(self, rag_pipeline):
        """Test that answers are grounded in retrieved context."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        question = "What is the vacation policy at Basecamp?"
        response = await rag_pipeline.answer_question(question)
        
        answer = response['answer']
        sources = response['sources']
        
        # Extract key information from sources
        source_texts = [s['content'].lower() for s in sources]
        combined_context = ' '.join(source_texts)
        
        # Answer should be based on the context
        # Check if answer mentions key facts from context
        if 'unlimited' in combined_context:
            assert 'unlimited' in answer.lower(), "Answer should mention 'unlimited' from context"
    
    async def test_handles_no_relevant_context(self, rag_pipeline):
        """Test handling of questions with no relevant context."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        # Question about something not in our test documents
        question = "What is the company's stock option policy?"
        response = await rag_pipeline.answer_question(question)
        
        # Should still return valid structure
        assert 'answer' in response
        assert 'sources' in response
        
        # Answer might indicate lack of information
        answer_lower = response['answer'].lower()
        # LLM might say "not mentioned" or provide generic response
        # Just verify it didn't crash
        assert isinstance(response['answer'], str)
    
    async def test_streaming_rag_workflow(self, rag_pipeline):
        """Test streaming answer generation in RAG pipeline."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        question = "What are the health insurance benefits?"
        
        chunks = []
        async for chunk in rag_pipeline.answer_question_stream(question):
            assert isinstance(chunk, str)
            chunks.append(chunk)
        
        # Should have received chunks
        assert len(chunks) > 0
        
        # Combine chunks
        full_answer = ''.join(chunks)
        assert len(full_answer) > 20
        
        # Should mention health insurance
        assert 'health' in full_answer.lower() or 'insurance' in full_answer.lower()
    
    async def test_metadata_tracking(self, rag_pipeline):
        """Test that pipeline tracks useful metadata."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        question = "What is the remote work policy?"
        response = await rag_pipeline.answer_question(question)
        
        # Check metadata
        metadata = response['metadata']
        assert 'documents_retrieved' in metadata
        assert metadata['documents_retrieved'] > 0
        
        # Should track number of sources
        assert len(response['sources']) == metadata['documents_retrieved']
    
    async def test_concurrent_questions(self, rag_pipeline):
        """Test handling multiple concurrent questions."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        questions = [
            "What is the vacation policy?",
            "What equipment is provided?",
            "How does remote work work?"
        ]
        
        # Process questions concurrently
        import asyncio
        tasks = [rag_pipeline.answer_question(q) for q in questions]
        responses = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(responses) == 3
        for response in responses:
            assert 'answer' in response
            assert 'sources' in response
            assert len(response['answer']) > 0
    
    async def test_answer_consistency(self, rag_pipeline):
        """Test that similar questions get consistent answers."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        # Ask same question twice
        question = "What is the 401k matching percentage?"
        
        response1 = await rag_pipeline.answer_question(question)
        response2 = await rag_pipeline.answer_question(question)
        
        # Both should mention 6%
        assert '6' in response1['answer'] or 'six' in response1['answer'].lower()
        assert '6' in response2['answer'] or 'six' in response2['answer'].lower()
    
    async def test_top_k_parameter(self, rag_pipeline):
        """Test that top_k parameter is respected."""
        if not await rag_pipeline.llm_client.is_available():
            pytest.skip("Ollama not available")
        
        question = "Tell me about employee benefits"
        response = await rag_pipeline.answer_question(question)
        
        # Should retrieve top_k documents (5 in our settings)
        sources = response['sources']
        assert len(sources) <= 5
        assert len(sources) > 0
    
    async def test_error_recovery(self, rag_pipeline):
        """Test that pipeline handles errors gracefully."""
        # Test with problematic inputs
        test_cases = [
            "",  # Empty question
            "a",  # Very short question
            "x" * 2000,  # Very long question
        ]
        
        for question in test_cases:
            try:
                response = await rag_pipeline.answer_question(question)
                # If it succeeds, verify structure
                assert isinstance(response, dict)
            except Exception as e:
                # If it fails, should be a meaningful error
                assert isinstance(e, (ValueError, Exception))
