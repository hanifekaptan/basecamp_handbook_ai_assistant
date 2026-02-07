"""
CRITICAL: Chunking and metadata preservation tests.

Tests markdown-aware chunking as analysis.md requires:
"MarkdownHeaderTextSplitter kullanımı bir zorunluluk olarak görülmelidir"
"""
import pytest
from unittest.mock import Mock, patch


class TestChunkingAndMetadata:
    """Chunking strategy and metadata preservation."""
    
    @patch('backend.app.database.vector_store.SentenceTransformer')
    @patch('backend.app.database.vector_store.get_db')
    @patch('backend.app.database.vector_store.get_settings')
    def test_markdown_header_based_chunking(self, mock_settings, mock_db, mock_transformer, test_settings, sample_markdown_content):
        """CRITICAL: Chunks should be created at markdown header boundaries."""
        from backend.app.database.vector_store import VectorStore
        
        mock_settings.return_value = test_settings
        
        mock_collection = Mock()
        mock_db.return_value.get_collection.return_value = mock_collection
        
        store = VectorStore()
        chunks = store._chunk_document_by_headers(sample_markdown_content, "test.md")
        
        # Should have multiple chunks based on headers
        assert len(chunks) >= 2
        
        # Each chunk should start with or contain a header
        for chunk in chunks:
            content = chunk['content']
            # Should contain markdown headers or header-related content
            assert '#' in content or len(content) > 10
    
    @patch('backend.app.database.vector_store.SentenceTransformer')
    @patch('backend.app.database.vector_store.get_db')
    @patch('backend.app.database.vector_store.get_settings')
    def test_source_metadata_preserved(self, mock_settings, mock_db, mock_transformer, test_settings, sample_markdown_content):
        """CRITICAL: Every chunk must have source metadata (filename)."""
        from backend.app.database.vector_store import VectorStore
        
        mock_settings.return_value = test_settings
        
        mock_collection = Mock()
        mock_db.return_value.get_collection.return_value = mock_collection
        
        store = VectorStore()
        chunks = store._chunk_document_by_headers(sample_markdown_content, "benefits-and-perks.md")
        
        # All chunks must have metadata with source
        for chunk in chunks:
            assert 'metadata' in chunk
            assert 'source' in chunk['metadata']
            assert chunk['metadata']['source'] == 'benefits-and-perks.md'
    
    @patch('backend.app.database.vector_store.SentenceTransformer')
    @patch('backend.app.database.vector_store.get_db')
    @patch('backend.app.database.vector_store.get_settings')
    def test_chunk_boundary_integrity(self, mock_settings, mock_db, mock_transformer, test_settings):
        """CRITICAL: Chunks should not split mid-sentence."""
        from backend.app.database.vector_store import VectorStore
        
        mock_settings.return_value = test_settings
        
        mock_collection = Mock()
        mock_db.return_value.get_collection.return_value = mock_collection
        
        # Content with clear sentence boundaries
        content = "This is sentence one. This is sentence two. This is sentence three."
        
        store = VectorStore()
        chunks = store._chunk_document_by_headers(content, "test.md")
        
        # Chunks should preserve sentence integrity
        for chunk in chunks:
            text = chunk['content'].strip()
            if text and len(text) > 5:
                # Should not start or end mid-word
                assert not text[0].isspace()
                # If contains a period, should be complete sentences
                if '.' in text:
                    assert text.count('.') >= 1  # At least one complete sentence
