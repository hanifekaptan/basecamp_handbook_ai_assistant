"""
Integration Tests: Vector Store & ChromaDB

Tests the real integration between:
- Sentence-transformers embedding model
- ChromaDB vector database
- Document indexing and retrieval pipeline

These tests use temporary ChromaDB instances to test real functionality
without affecting production data.
"""
import pytest
import tempfile
import shutil
import os
from pathlib import Path
from backend.app.database.vector_store import VectorStore
from backend.app.core.config import Settings

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


@pytest.fixture
def temp_docs_dir():
    """Create temporary directory with test markdown files."""
    temp_dir = tempfile.mkdtemp()
    docs_path = Path(temp_dir)
    
    # Create test markdown files
    (docs_path / "benefits.md").write_text("""
# Employee Benefits

## Health Insurance
We offer comprehensive health insurance to all full-time employees.
Coverage includes medical, dental, and vision.

## Vacation Policy
Employees receive 15 days of paid vacation per year.
Vacation days accumulate monthly at a rate of 1.25 days per month.

## Retirement Plan
We provide 401(k) matching up to 5% of your salary.
    """)
    
    (docs_path / "remote-work.md").write_text("""
# Remote Work Policy

## Work from Anywhere
All employees can work remotely full-time or hybrid.

## Equipment
We provide laptops, monitors, and home office equipment.
Submit requests through the IT portal.

## Communication
Use Slack for daily communication and Zoom for video calls.
    """)
    
    yield docs_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_chroma_dir():
    """Create temporary ChromaDB directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Windows fix: ignore errors if files are locked by ChromaDB
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def integration_settings(temp_docs_dir, temp_chroma_dir):
    """Settings for integration tests with temp directories."""
    return Settings(
        chroma_persist_directory=temp_chroma_dir,
        chroma_collection_name="test_integration_collection",
        embedding_model="all-MiniLM-L6-v2",
        docs_directory=str(temp_docs_dir),
        chunk_size=512,
        chunk_overlap=50,
        top_k_results=3
    )


class TestVectorStoreIntegration:
    """Integration tests for VectorStore with real ChromaDB and embeddings."""
    
    def test_vector_store_initialization(self, integration_settings, monkeypatch):
        """Test VectorStore initializes with real embedding model and ChromaDB."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        
        # Verify embedding model loaded
        assert vector_store.embedding_model is not None
        assert hasattr(vector_store.embedding_model, 'encode')
        
        # Verify ChromaDB connection initialized
        assert vector_store.db is not None
        assert vector_store.collection is not None
        
        # Collection should start empty
        stats = vector_store.get_collection_stats()
        assert stats['total_documents'] == 0
    
    def test_document_indexing_end_to_end(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test full document indexing pipeline with real embedding generation."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        
        # Index documents
        indexed_count = vector_store.index_documents(str(temp_docs_dir))
        
        # Should have indexed multiple chunks
        assert indexed_count > 0
        
        # Verify documents are in the database
        stats = vector_store.get_collection_stats()
        assert stats['total_documents'] == indexed_count
        
        # Verify we can retrieve document count
        assert indexed_count >= 6  # At least 6 chunks from our test docs
    
    def test_semantic_search_accuracy(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test semantic search returns relevant documents."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        vector_store.index_documents(str(temp_docs_dir))
        
        # Search for vacation policy
        results = vector_store.search("vacation policy", top_k=3)
        
        # Should return results
        assert len(results) > 0
        assert len(results) <= 3
        
        # First result should be about vacation
        top_result = results[0]
        assert 'content' in top_result
        assert 'metadata' in top_result
        assert 'relevance_score' in top_result
        
        # Content should mention vacation
        content_lower = top_result['content'].lower()
        assert 'vacation' in content_lower or 'paid' in content_lower
        
        # Score should be reasonable
        assert 0.0 <= top_result['relevance_score'] <= 1.0
        assert top_result['relevance_score'] > 0.5  # Should be reasonably relevant
    
    def test_search_different_queries(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test search works for different query types."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        vector_store.index_documents(str(temp_docs_dir))
        
        # Test different queries
        queries = [
            ("health insurance", "health"),
            ("remote work equipment", "equipment"),
            ("401k retirement", "401"),
        ]
        
        for query, expected_keyword in queries:
            results = vector_store.search(query, top_k=2)
            assert len(results) > 0, f"No results for query: {query}"
            
            # At least one result should mention the expected keyword
            found = any(expected_keyword.lower() in r['content'].lower() for r in results)
            assert found, f"Expected keyword '{expected_keyword}' not found in results for '{query}'"
    
    def test_metadata_preservation(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test that metadata is preserved through indexing and retrieval."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        vector_store.index_documents(str(temp_docs_dir))
        
        results = vector_store.search("employee benefits", top_k=3)
        
        # Each result should have proper metadata
        for result in results:
            metadata = result['metadata']
            
            # Should have source file
            assert 'source' in metadata
            assert metadata['source'].endswith('.md')
            
            # Should have at least one header
            assert 'Header 1' in metadata or 'Header 2' in metadata
    
    def test_relevance_score_ordering(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test that results are ordered by relevance score."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        vector_store.index_documents(str(temp_docs_dir))
        
        results = vector_store.search("vacation days", top_k=5)
        
        # Results should be ordered by descending relevance
        scores = [r['relevance_score'] for r in results]
        assert scores == sorted(scores, reverse=True), "Results not ordered by relevance"
    
    def test_chunking_with_headers(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test that document chunking preserves header structure."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        vector_store.index_documents(str(temp_docs_dir))
        
        # Search for specific section
        results = vector_store.search("health insurance coverage", top_k=2)
        
        assert len(results) > 0
        top_result = results[0]
        
        # Should have header metadata
        metadata = top_result['metadata']
        assert 'Header 1' in metadata or 'Header 2' in metadata
        
        # Header should relate to benefits/health
        headers_text = ' '.join([
            metadata.get('Header 1', ''),
            metadata.get('Header 2', ''),
            metadata.get('Header 3', '')
        ]).lower()
        
        assert any(keyword in headers_text for keyword in ['benefit', 'health', 'insurance'])
    
    def test_empty_query_handling(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test handling of edge cases like empty queries."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        vector_store.index_documents(str(temp_docs_dir))
        
        # Empty query should return empty results or raise appropriate error
        results = vector_store.search("", top_k=3)
        
        # Should handle gracefully (either empty results or valid results)
        assert isinstance(results, list)
    
    def test_top_k_parameter_respected(self, integration_settings, temp_docs_dir, monkeypatch):
        """Test that top_k parameter limits results correctly."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        vector_store = VectorStore()
        vector_store.index_documents(str(temp_docs_dir))
        
        # Test different top_k values
        for k in [1, 3, 5]:
            results = vector_store.search("employee", top_k=k)
            assert len(results) <= k, f"Returned more than top_k={k} results"
    
    def test_collection_persistence(self, integration_settings, temp_docs_dir, temp_chroma_dir, monkeypatch):
        """Test that ChromaDB persists data between instances."""
        monkeypatch.setattr('backend.app.database.vector_store.get_settings', lambda: integration_settings)
        monkeypatch.setattr('backend.app.database.connection.get_settings', lambda: integration_settings)
        
        # First instance: index documents
        vector_store1 = VectorStore()
        indexed_count = vector_store1.index_documents(str(temp_docs_dir))
        assert indexed_count > 0
        
        # Create new instance with same persist directory
        vector_store2 = VectorStore()
        
        # Should still have the indexed documents
        stats = vector_store2.get_collection_stats()
        assert stats['total_documents'] == indexed_count
        
        # Should still be able to search
        results = vector_store2.search("vacation", top_k=3)
        assert len(results) > 0
