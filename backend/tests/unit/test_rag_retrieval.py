"""
CRITICAL: RAG retrieval quality tests.

Tests retrieval accuracy as analysis.md states:
"RAG sistemlerinde başarının %80'i geri getirilen verinin kalitesine bağlıdır"
"""
import pytest
from unittest.mock import Mock, patch


class TestRAGRetrieval:
    """Retrieval quality - the 80% of RAG success."""
    
    @patch('backend.app.database.vector_store.SentenceTransformer')
    @patch('backend.app.database.vector_store.get_db')
    @patch('backend.app.database.vector_store.get_settings')
    def test_relevant_documents_retrieved(self, mock_settings, mock_db, mock_transformer, test_settings, mock_embedding_model):
        """CRITICAL: Search should return relevant documents."""
        from backend.app.database.vector_store import VectorStore
        
        mock_settings.return_value = test_settings
        
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [['Vacation policy: 15 days per year']],
            'metadatas': [[{'source': 'benefits-and-perks.md'}]],
            'distances': [[0.15]]  # Low distance = high relevance
        }
        mock_db.return_value.get_collection.return_value = mock_collection
        
        mock_transformer.return_value = mock_embedding_model
        
        store = VectorStore()
        results = store.search("vacation policy")
        
        assert len(results) > 0
        assert results[0]['content'] == 'Vacation policy: 15 days per year'
        assert results[0]['metadata']['source'] == 'benefits-and-perks.md'
    
    @patch('backend.app.database.vector_store.SentenceTransformer')
    @patch('backend.app.database.vector_store.get_db')
    @patch('backend.app.database.vector_store.get_settings')
    def test_relevance_score_threshold(self, mock_settings, mock_db, mock_transformer, test_settings, mock_embedding_model):
        """CRITICAL: Relevance scores should be meaningful (>0.7 for good matches)."""
        from backend.app.database.vector_store import VectorStore
        
        mock_settings.return_value = test_settings
        
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [['Vacation: 15 days', 'Health insurance info']],
            'metadatas': [[{'source': 'benefits.md'}, {'source': 'other.md'}]],
            'distances': [[0.2, 0.8]]  # First is relevant, second is not
        }
        mock_db.return_value.get_collection.return_value = mock_collection
        
        mock_transformer.return_value = mock_embedding_model
        
        store = VectorStore()
        results = store.search("vacation days", top_k=2)
        
        # First result should have high score, second low
        assert results[0]['relevance_score'] > 0.7
        assert results[1]['relevance_score'] < 0.7  # More lenient threshold
    
    @patch('backend.app.database.vector_store.SentenceTransformer')
    @patch('backend.app.database.vector_store.get_db')
    @patch('backend.app.database.vector_store.get_settings')
    def test_top_k_parameter_respected(self, mock_settings, mock_db, mock_transformer, test_settings, mock_embedding_model):
        """CRITICAL: top_k parameter should control result count."""
        from backend.app.database.vector_store import VectorStore
        
        mock_settings.return_value = test_settings
        
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [['Doc1', 'Doc2', 'Doc3']],
            'metadatas': [[{'source': 'a.md'}, {'source': 'b.md'}, {'source': 'c.md'}]],
            'distances': [[0.1, 0.2, 0.3]]
        }
        mock_db.return_value.get_collection.return_value = mock_collection
        
        mock_transformer.return_value = mock_embedding_model
        
        store = VectorStore()
        results = store.search("test", top_k=3)
        
        assert len(results) == 3
        # Verify query was called with correct top_k
        mock_collection.query.assert_called_once()
        assert mock_collection.query.call_args[1]['n_results'] == 3
