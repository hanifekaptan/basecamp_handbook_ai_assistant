# API Schemas

Detailed schemas for all API request and response models.

## Request Models

### QuestionRequest

Used for `/ask` and `/ask/stream` endpoints.

```python
class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The question to ask"
    )
```

**JSON Schema**:
```json
{
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1000,
            "description": "The question to ask"
        }
    },
    "required": ["question"]
}
```

**Example**:
```json
{
    "question": "What health insurance benefits does Basecamp offer?"
}
```

**Validation Rules**:
- `question`: Must be 1-1000 characters

---

## Response Models

### QuestionResponse

Response from `/ask` endpoint.

```python
class QuestionResponse(BaseModel):
    answer: str = Field(description="The generated answer")
    sources: List[SourceDocument] = Field(description="Source documents used")
    question: str = Field(description="Original question")
    metadata: Dict[str, Any] = Field(description="Additional metadata")
```
```

**JSON Schema**:
```json
{
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
            "description": "The generated answer"
        },
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Source text chunk"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Document metadata",
                        "properties": {
                            "source": {"type": "string"},
                            "Header 1": {"type": "string"},
                            "Header 2": {"type": "string"},
                            "Header 3": {"type": "string"}
                        }
                    },
                    "score": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Relevance score"
                    }
                }
            }
        },
        "model": {
            "type": "string",
            "description": "LLM model used"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp"
        }
    }
}
```

**Example**:
```json
{
    "answer": "Basecamp offers comprehensive health insurance including medical, dental, and vision coverage for all full-time employees. The company covers 100% of the premium for employees and 75% for dependents.",
    "sources": [
        {
            "text": "We provide comprehensive health insurance to all full-time employees. Coverage includes medical, dental, and vision. Basecamp pays 100% of premiums for employees and 75% for dependents.",
            "metadata": {
                "source": "benefits-and-perks.md",
                "Header 1": "Benefits and Perks",
                "Header 2": "Health Insurance",
                "chunk_id": "42"
            },
            "score": 0.94
        },
        {
            "text": "Health insurance eligibility begins on your first day of employment. You'll receive information about plan options during onboarding.",
            "metadata": {
                "source": "getting-started.md",
                "Header 1": "Getting Started",
                "Header 2": "Benefits Enrollment",
                "chunk_id": "18"
            },
            "score": 0.87
        }
    ],
    "model": "llama3.2:3b",
    "timestamp": "2026-01-20T10:30:45.123456Z"
}
```

---

### HealthResponse

Response from `/health` endpoint.

```python
class HealthResponse(BaseModel):
    status: str = Field(description="Health status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Check timestamp")
    ollama_available: bool = Field(description="Ollama availability")
    ollama_model: str = Field(description="LLM model name")
    documents_indexed: int = Field(description="Number of indexed documents")
    collections: List[str] = Field(description="Database collections")
```

**Example**:
```json
{
    "status": "healthy",
    "version": "2.0.0",
    "timestamp": "2026-01-20T10:30:45.123456Z",
    "ollama_available": true,
    "ollama_model": "llama3.2:3b",
    "documents_indexed": 150,
    "collections": ["basecamp_handbook"]
}
```

---

### StatsResponse

Response from `/metrics/system` endpoint.

```python
class StatsResponse(BaseModel):
    total_documents: int = Field(description="Total document files")
    total_chunks: int = Field(description="Total indexed chunks")
    collections: List[str] = Field(description="Database collections")
    embedding_model: str = Field(description="Embedding model name")
    embedding_dimension: int = Field(description="Embedding vector size")
    llm_model: str = Field(description="LLM model name")
    chunk_size: int = Field(description="Chunk size setting")
    chunk_overlap: int = Field(description="Chunk overlap setting")
    top_k_results: int = Field(description="Search result count")
```

**Example**:
```json
{
    "total_documents": 15,
    "total_chunks": 150,
    "collections": ["basecamp_handbook"],
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "llm_model": "llama3.2:3b",
    "chunk_size": 800,
    "chunk_overlap": 200,
    "top_k_results": 5
}
```

---

## Error Models

### ErrorResponse

Generic error response format.

```python
class ErrorDetail(BaseModel):
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    timestamp: str = Field(description="Error timestamp")

class ErrorResponse(BaseModel):
    detail: ErrorDetail
```

**Example**:
```json
{
    "detail": {
        "error": "ValidationError",
        "message": "Question must be between 3 and 500 characters",
        "timestamp": "2026-01-20T10:30:45.123456Z"
    }
}
```

---

## Data Types

### Metadata Fields

Common metadata fields in source documents:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `source` | string | Source filename | `"benefits-and-perks.md"` |
| `Header 1` | string | Top-level header | `"Benefits and Perks"` |
| `Header 2` | string | Second-level header | `"Health Insurance"` |
| `Header 3` | string | Third-level header | `"Dental Coverage"` |
| `chunk_id` | string | Unique chunk identifier | `"42"` |

---

## Validation Examples

### Valid Requests

✅ **Valid request**:
```json
{
    "question": "What health insurance benefits does Basecamp offer to employees and their families?"
}
```

### Invalid Requests

❌ **Question too short**:
```json
{
    "question": "Hi"
}
```
Error: `Question must be at least 3 characters`

❌ **Question too long**:
```json
{
    "question": "What is the vacation policy and how does it work and what are the rules and can I take time off whenever I want and do I need approval and how much notice should I give and what happens if I take too much vacation and is there a maximum and what about holidays and sick days and personal days and family leave and parental leave and bereavement leave and jury duty and voting time and military leave and sabbaticals and unpaid leave and emergency situations and last minute requests and international travel?"
}
```
Error: `Question must be at most 1000 characters`

❌ **Missing question**:
```json
{}
```
Error: `Field required: question`

---

## Type Definitions (TypeScript)

For frontend developers:

```typescript
// Request types
interface QuestionRequest {
  question: string;  // 1-1000 chars
}

// Response types
interface SourceDocument {
  text: string;
  metadata: {
    source: string;
    'Header 1'?: string;
    'Header 2'?: string;
    'Header 3'?: string;
    chunk_id?: string;
  };
  score: number;  // 0-1
}

interface QuestionResponse {
  answer: string;
  sources: SourceDocument[];
  model: string;
  timestamp: string;  // ISO 8601
}

interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  timestamp: string;
  ollama_available: boolean;
  ollama_model: string;
  documents_indexed: number;
  collections: string[];
}

interface ReindexResponse {
  status: 'success' | 'error';
  message: string;
  indexed_count: number;
  files_processed: number;
  duration_seconds: number;
}

interface StatsResponse {
  total_documents: number;
  total_chunks: number;
  collections: string[];
  embedding_model: string;
  embedding_dimension: number;
  llm_model: string;
  chunk_size: number;
  chunk_overlap: number;
  top_k_results: number;
}

interface ErrorResponse {
  detail: {
    error: string;
    message: string;
    timestamp: string;
  };
}
```

---

## OpenAPI Schema

The complete OpenAPI 3.0 schema is available at:

```
http://localhost:8000/openapi.json
```

You can use this to generate client libraries in any language:

```bash
# Generate TypeScript client
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./client

# Generate Python client
pip install openapi-python-client
openapi-python-client generate \
  --url http://localhost:8000/openapi.json
```

---

## Next Steps

- [API Endpoints](endpoints.md) - Full endpoint documentation
- [API Examples](examples.md) - More usage examples
- [Quick Start](../quick-start.md) - Get started quickly

---

**Schema Summary**:

| Model | Type | Used In |
|-------|------|---------|
| `QuestionRequest` | Request | `/ask`, `/ask/stream` |
| `QuestionResponse` | Response | `/ask` |
| `HealthResponse` | Response | `/health` |

| `ErrorResponse` | Response | All error cases |
