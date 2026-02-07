"""
Integration Tests Package

Integration tests verify that multiple components work together correctly.
Unlike unit tests (which test components in isolation), integration tests:
- Use real services (ChromaDB, Ollama)
- Test actual data flow between components
- Verify end-to-end functionality

Test Categories:
- test_vector_store_integration: ChromaDB + embeddings
- test_llm_integration: Ollama LLM client
- test_rag_pipeline_integration: Complete RAG workflow
- test_api_services_integration: API endpoints with real services

Running Integration Tests:
    # All integration tests
    pytest backend/tests/integration/
    
    # Specific test file
    pytest backend/tests/integration/test_vector_store_integration.py
    
    # With verbose output
    pytest backend/tests/integration/ -v
    
    # Skip if Ollama not available
    pytest backend/tests/integration/ -v || echo "Some tests require Ollama"

Requirements:
- Ollama must be running for LLM tests
- Tests use temporary directories (no data pollution)
- Tests are safe to run in development
"""
