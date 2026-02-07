"""
Shared test fixtures and configuration.

Provides mock objects for RAG components to enable fast, isolated testing.
"""
import pytest
import numpy as np
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Disable ChromaDB telemetry to avoid errors in tests
os.environ["ANONYMIZED_TELEMETRY"] = "False"


@pytest.fixture
def test_settings():
    """Test settings with real values instead of MagicMock."""
    from backend.app.core.config import Settings
    return Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.1:8b",
        chroma_persist_directory="./test_chroma",
        chroma_collection_name="test_collection",
        embedding_model="all-MiniLM-L6-v2",
        docs_directory="./test_docs",
        chunk_size=512,
        chunk_overlap=50,
        top_k_results=3,
        temperature=0.3
    )


@pytest.fixture
def test_client():
    """FastAPI test client."""
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model that returns numpy arrays."""
    mock = Mock()
    # Return numpy array instead of list
    mock.encode.return_value = np.array([[0.1] * 384])
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore for testing retrieval."""
    mock = Mock()
    mock.search.return_value = [
        {
            'content': 'Employees get 15 days of vacation per year.',
            'metadata': {'source': 'benefits-and-perks.md', 'chunk_index': 0},
            'relevance_score': 0.85
        },
        {
            'content': 'Vacation days accumulate monthly.',
            'metadata': {'source': 'benefits-and-perks.md', 'chunk_index': 1},
            'relevance_score': 0.78
        }
    ]
    mock.index_documents.return_value = 202
    mock.get_stats.return_value = {'total_documents': 202}
    return mock


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing generation."""
    mock = Mock()
    mock.is_available = AsyncMock(return_value=True)
    mock.generate_answer = AsyncMock(
        return_value="Based on the handbook, employees get 15 days of vacation per year. (Source: benefits-and-perks.md)"
    )
    
    async def mock_stream():
        chunks = ["Based on ", "the handbook, ", "employees get ", "15 days ", "of vacation. ", "(Source: benefits-and-perks.md)"]
        for chunk in chunks:
            yield chunk
    
    mock.generate_answer_stream = mock_stream
    return mock


@pytest.fixture
def mock_rag_pipeline(mock_vector_store, mock_llm_client):
    """Mock complete RAG pipeline."""
    mock = Mock()
    mock.vector_store = mock_vector_store
    mock.llm_client = mock_llm_client
    mock.answer_question = AsyncMock(
        return_value={
            'answer': 'Employees get 15 days of vacation per year.',
            'sources': [
                {
                    'content': 'Employees get 15 days of vacation per year.',
                    'source': 'benefits-and-perks.md',
                    'relevance_score': 0.85
                }
            ],
            'confidence': 0.85
        }
    )
    
    async def mock_stream_answer():
        chunks = ["Employees ", "get 15 days ", "of vacation. ", "(Source: benefits-and-perks.md)"]
        for chunk in chunks:
            yield chunk
    
    mock.answer_question_stream = mock_stream_answer
    mock.get_status = AsyncMock(return_value={
        'vector_db': 'healthy',
        'llm': 'healthy',
        'documents_indexed': 202
    })
    return mock


@pytest.fixture
def sample_markdown_content():
    """Sample markdown document for chunking tests."""
    return """# Benefits and Perks

## Vacation Policy
Employees receive 15 days of vacation per year. Vacation days accumulate monthly at a rate of 1.25 days per month.

## Health Insurance
Full health insurance coverage is provided to all full-time employees.

### Dental Coverage
Dental coverage is included as part of the health insurance package.
"""


@pytest.fixture
def sample_chunks():
    """Expected chunks from sample markdown."""
    return [
        {
            'content': '# Benefits and Perks\n\n## Vacation Policy\nEmployees receive 15 days of vacation per year.',
            'metadata': {'source': 'test.md', 'chunk_index': 0, 'header': 'Benefits and Perks > Vacation Policy'}
        },
        {
            'content': '## Health Insurance\nFull health insurance coverage is provided to all full-time employees.',
            'metadata': {'source': 'test.md', 'chunk_index': 1, 'header': 'Benefits and Perks > Health Insurance'}
        }
    ]


@pytest.fixture(autouse=True)
def reset_settings_cache():
    """Reset settings cache between tests."""
    from backend.app.core.config import Settings
    Settings._instance = None
    yield
    Settings._instance = None
