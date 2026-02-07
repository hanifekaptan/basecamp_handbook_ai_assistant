# Test Suite Documentation

Comprehensive test coverage for the Basecamp Handbook RAG API.

## Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (isolated components)
│   ├── test_vector_db.py
│   ├── test_rag_retrieval.py
│   ├── test_input_validation.py
│   ├── test_grounding.py
│   ├── test_error_handling.py
│   └── test_chunking_metadata.py
├── integration/             # Integration tests (real services)
│   ├── test_vector_store_integration.py
│   ├── test_llm_integration.py
│   ├── test_rag_pipeline_integration.py
│   └── test_api_services_integration.py
└── functional/              # E2E tests (complete workflows)
    └── test_e2e_critical.py
```

## Test Categories

### 1. Unit Tests (`unit/`)
**Purpose**: Test individual components in isolation using mocks.

- **Fast**: Run in milliseconds
- **No dependencies**: Don't require Ollama or external services
- **High coverage**: Test edge cases and error conditions

**Example**:
```bash
pytest backend/tests/unit/ -v
```

### 2. Integration Tests (`integration/`)
**Purpose**: Test how components work together with real services.

- **Real services**: Use actual ChromaDB, Ollama, embeddings
- **Isolated data**: Use temporary directories
- **Requires Ollama**: Most tests need Ollama running

**Key Tests**:
- `test_vector_store_integration.py` - ChromaDB + embeddings integration
- `test_llm_integration.py` - Ollama LLM client integration
- `test_rag_pipeline_integration.py` - Complete RAG pipeline
- `test_api_services_integration.py` - API endpoints with real services

**Example**:
```bash
# Ensure Ollama is running
ollama serve

# Run integration tests
pytest backend/tests/integration/ -v
```

### 3. Functional Tests (`functional/`)
**Purpose**: End-to-end tests of complete user workflows.

- **API-level**: Test through HTTP endpoints
- **Complete scenarios**: Full request/response cycles
- **Critical paths**: Core functionality testing

**Example**:
```bash
pytest backend/tests/functional/ -v
```

## Running Tests

### Prerequisites

1. **Python Environment**:
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install pytest pytest-asyncio
   ```

2. **For Integration Tests**:
   ```bash
   # Start Ollama
   ollama serve
   
   # Pull the model
   ollama pull llama3.2:3b
   ```

### Run All Tests

```bash
# From project root
pytest backend/tests/ -v

# With coverage
pytest backend/tests/ --cov=backend/app --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only (fast, no dependencies)
pytest backend/tests/unit/ -v

# Integration tests only (requires Ollama)
pytest backend/tests/integration/ -v

# Functional/E2E tests
pytest backend/tests/functional/ -v
```

### Run Specific Test Files

```bash
# Vector store integration
pytest backend/tests/integration/test_vector_store_integration.py -v

# LLM integration
pytest backend/tests/integration/test_llm_integration.py -v

# RAG pipeline
pytest backend/tests/integration/test_rag_pipeline_integration.py -v

# API services
pytest backend/tests/integration/test_api_services_integration.py -v
```

### Run Specific Tests

```bash
# Single test
pytest backend/tests/integration/test_vector_store_integration.py::TestVectorStoreIntegration::test_semantic_search_accuracy -v

# Tests matching pattern
pytest backend/tests/ -k "search" -v
```

### Useful Options

```bash
# Verbose output
pytest backend/tests/ -v

# Show print statements
pytest backend/tests/ -s

# Stop on first failure
pytest backend/tests/ -x

# Run last failed tests
pytest backend/tests/ --lf

# Show slowest tests
pytest backend/tests/ --durations=10

# Parallel execution (install pytest-xdist)
pytest backend/tests/unit/ -n auto
```

## Integration Test Details

### test_vector_store_integration.py

**Tests**: ChromaDB + sentence-transformers integration

**Key Scenarios**:
- ✅ Vector store initialization
- ✅ Document indexing pipeline
- ✅ Semantic search accuracy
- ✅ Metadata preservation
- ✅ Relevance score ordering
- ✅ Chunking with header structure
- ✅ Collection persistence

**Requirements**: None (uses temp directories)

**Runtime**: ~15-30 seconds

### test_llm_integration.py

**Tests**: Ollama LLM client functionality

**Key Scenarios**:
- ✅ Ollama availability check
- ✅ Simple text generation
- ✅ Context-based generation
- ✅ Streaming responses
- ✅ Temperature effects
- ✅ Prompt following
- ✅ Error handling
- ✅ Grounding in context

**Requirements**: Ollama running with llama3.2:3b

**Runtime**: ~30-60 seconds (depends on LLM speed)

### test_rag_pipeline_integration.py

**Tests**: Complete RAG workflow

**Key Scenarios**:
- ✅ Pipeline initialization
- ✅ Complete RAG workflow (retrieve → prompt → generate)
- ✅ Different question types
- ✅ Source attribution
- ✅ Answer grounding
- ✅ Streaming generation
- ✅ Metadata tracking
- ✅ Concurrent questions
- ✅ Answer consistency

**Requirements**: Ollama running + temp directories

**Runtime**: ~60-120 seconds

### test_api_services_integration.py

**Tests**: API endpoints with real services

**Key Scenarios**:
- ✅ Health endpoint with real services
- ✅ Ask endpoint complete workflow
- ✅ Input validation
- ✅ Streaming endpoint
- ✅ Metrics endpoints (performance, usage, system)
- ✅ Rate limiting enforcement
- ✅ Concurrent requests
- ✅ Response timing
- ✅ API documentation accessibility

**Requirements**: Ollama running

**Runtime**: ~60-90 seconds

## Troubleshooting

### "Ollama not available"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve

# Verify model is available
ollama list | grep llama3.2
```

### "Collection already exists"

Integration tests use temporary directories, but if you see this error:

```bash
# Clean up any test ChromaDB directories
rm -rf /tmp/tmp*
```

### "No module named 'backend'"

Ensure you're running from the project root and PYTHONPATH is set:

```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest backend/tests/
```

### Tests are slow

Integration tests are slower because they use real services:

- **Unit tests**: 5-10 seconds (fast, use mocks)
- **Integration tests**: 2-5 minutes (real services)
- **Functional tests**: 1-3 minutes (API calls)

To speed up:
```bash
# Run only fast unit tests
pytest backend/tests/unit/ -v

# Run integration tests in parallel (install pytest-xdist)
pytest backend/tests/integration/ -n 2
```

## Test Coverage

Check test coverage:

```bash
# Generate coverage report
pytest backend/tests/ --cov=backend/app --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

Current coverage targets:
- **Unit tests**: 80%+ coverage
- **Integration tests**: Critical paths covered
- **Functional tests**: All API endpoints tested

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run unit tests
      run: pytest backend/tests/unit/ -v --cov
    
    # Integration tests would require Ollama setup
    # - name: Setup Ollama
    #   run: |
    #     # Install and configure Ollama
    #
    # - name: Run integration tests
    #   run: pytest backend/tests/integration/ -v
```

## Writing New Tests

### Unit Test Template

```python
"""Test module description."""
import pytest
from backend.app.your_module import YourClass

class TestYourClass:
    """Test suite for YourClass."""
    
    def test_basic_functionality(self):
        """Test description."""
        obj = YourClass()
        result = obj.method()
        assert result == expected_value
```

### Integration Test Template

```python
"""Integration test description."""
import pytest
from backend.app.your_module import YourClass

@pytest.fixture
def integration_setup():
    """Setup for integration test."""
    # Setup real resources
    yield resource
    # Cleanup

@pytest.mark.asyncio
class TestYourClassIntegration:
    """Integration tests for YourClass."""
    
    async def test_with_real_service(self, integration_setup):
        """Test with real service."""
        obj = YourClass(integration_setup)
        result = await obj.async_method()
        assert result is not None
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use Fixtures**: Share setup code with fixtures
5. **Mock External Services**: In unit tests, always mock
6. **Test Edge Cases**: Include error conditions
7. **Keep Tests Fast**: Unit tests should run quickly
8. **Document Requirements**: Note when tests need Ollama

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
