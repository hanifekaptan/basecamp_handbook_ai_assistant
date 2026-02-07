# API Endpoints

Complete reference for all API endpoints in the Basecamp Handbook RAG API.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication (development mode).

!!! warning "Production Deployment"
    For production use, implement authentication (JWT, OAuth2, API keys).

---

## Health Check

### GET /health

Check system health and availability.

**Request**:
```http
GET /api/v1/health HTTP/1.1
Host: localhost:8000
```

**Response**:
```json
{
    "status": "healthy",
    "version": "2.0.0",
    "timestamp": "2026-01-20T10:30:45.123Z",
    "ollama_available": true,
    "ollama_model": "llama3.2:3b",
    "documents_indexed": 150,
    "collections": ["basecamp_handbook"]
}
```

**Status Codes**:
- `200 OK` - System is healthy
- `503 Service Unavailable` - Ollama is not available

**cURL Example**:
```bash
curl http://localhost:8000/api/v1/health
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/api/v1/health")
health = response.json()

if health["status"] == "healthy":
    print(f"✅ System healthy with {health['documents_indexed']} documents")
else:
    print("❌ System unhealthy")
```

---

## Question Answering

### POST /ask

Ask a question and receive a complete answer.

**Request**:
```http
POST /api/v1/ask HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
    "question": "What is Basecamp's vacation policy?"
}
```

**Request Body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | The question to ask (1-1000 chars) |

**Response**:
```json
{
    "answer": "Basecamp offers unlimited vacation time to all full-time employees. Time off should be coordinated with your team to ensure coverage. There's no formal approval process, but employees are expected to be responsible and ensure their work is covered.",
    "sources": [
        {
            "text": "Basecamp offers unlimited vacation to all full-time employees. We trust you to take the time you need...",
            "metadata": {
                "source": "benefits-and-perks.md",
                "Header 1": "Benefits",
                "Header 2": "Vacation Policy"
            },
            "score": 0.92
        },
        {
            "text": "When taking time off, coordinate with your team to ensure coverage...",
            "metadata": {
                "source": "how-we-work.md",
                "Header 1": "Working Together",
                "Header 2": "Time Off"
            },
            "score": 0.87
        }
    ],
    "model": "llama3.2:3b",
    "timestamp": "2026-01-20T10:30:45.123Z"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | The generated answer |
| `sources` | array | Relevant context chunks with metadata |
| `question` | string | Original question |
| `metadata` | object | Additional information (documents_retrieved, confidence) |

**Status Codes**:
- `200 OK` - Success
- `400 Bad Request` - Invalid request body
- `503 Service Unavailable` - LLM service unavailable

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the vacation policy?"}'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "question": "What health insurance does Basecamp offer?"
    }
)

data = response.json()
print(f"Answer: {data['answer']}\n")
print(f"Sources ({len(data['sources'])}):")
for i, source in enumerate(data['sources'], 1):
    print(f"  [{i}] {source['metadata']['source']} (score: {source['score']:.2f})")
```

**JavaScript Example**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What is the vacation policy?'
  })
});

const data = await response.json();
console.log('Answer:', data.answer);
console.log('Sources:', data.sources.length);
```

---

### POST /ask/stream

Ask a question with real-time streaming response.

**Request**:
```http
POST /api/v1/ask/stream HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Accept: text/event-stream

{
    "question": "What is Basecamp's vacation policy?"
}
```

**Response** (Server-Sent Events):
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: Basecamp

data:  offers

data:  unlimited

data:  vacation

data:  time

data: ...

```

**Status Codes**:
- `200 OK` - Stream started
- `400 Bad Request` - Invalid request
- `503 Service Unavailable` - LLM unavailable

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v1/ask/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -N \
  -d '{"question": "What is the vacation policy?"}'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ask/stream",
    json={"question": "What is the vacation policy?"},
    stream=True
)

full_answer = ""
for line in response.iter_lines():
    if line:
        token = line.decode('utf-8').replace('data: ', '')
        full_answer += token
        print(token, end='', flush=True)

print(f"\n\nComplete answer: {full_answer}")
```

**JavaScript Example**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/ask/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What is the vacation policy?'
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const token = line.slice(6);
      process.stdout.write(token);
    }
  }
}
```

---

## Metrics

### GET /metrics/performance

Get system performance metrics.

**Request**:
```http
GET /api/v1/metrics/performance HTTP/1.1
Host: localhost:8000
```

**Response**:
```json
{
    "avg_response_time_ms": 2341,
    "min_response_time_ms": 1823,
    "max_response_time_ms": 4102,
    "llm_performance": {
        "avg_generation_time_ms": 2134,
        "avg_tokens_per_second": 14.8
    },
    "vector_search_performance": {
        "avg_search_time_ms": 187
    }
}
```

### GET /metrics/usage

Get usage statistics.

**Request**:
```http
GET /api/v1/metrics/usage HTTP/1.1
Host: localhost:8000
```

**Response**:
```json
{
    "total_queries": 142,
    "success_rate": 97.2,
    "query_distribution": {
        "success": 138,
        "error": 4
    }
}
```

### GET /metrics/system

Get system resource usage.

**Request**:
```http
GET /api/v1/metrics/system HTTP/1.1
Host: localhost:8000
```

**Response**:
```json
{
    "cpu_percent": 23.4,
    "memory_percent": 45.2,
    "disk_percent": 67.8,
    "uptime_seconds": 3600,
    "process": {
        "memory_mb": 2048,
        "threads": 8
    }
}
```

---

## Interactive Documentation

### Swagger UI

Access interactive API documentation with try-it-out functionality:

```
http://localhost:8000/docs
```

Features:
- Test all endpoints directly in browser
- See request/response schemas
- View detailed parameter descriptions
- Execute requests with custom data

### ReDoc

Alternative documentation with better readability:

```
http://localhost:8000/redoc
```

---

## Error Responses

All errors follow a consistent format:

```json
{
    "detail": {
        "error": "ErrorType",
        "message": "Human-readable error message",
        "timestamp": "2026-01-20T10:30:45.123Z"
    }
}
```

### Common Errors

#### 400 Bad Request

Invalid request parameters:

```json
{
    "detail": {
        "error": "ValidationError",
        "message": "Question must be between 3 and 500 characters",
        "timestamp": "2026-01-20T10:30:45.123Z"
    }
}
```

#### 503 Service Unavailable

Ollama is not running:

```json
{
    "detail": {
        "error": "ServiceUnavailable",
        "message": "Ollama LLM service is not available. Please ensure Ollama is running.",
        "timestamp": "2026-01-20T10:30:45.123Z"
    }
}
```

#### 500 Internal Server Error

Unexpected server error:

```json
{
    "detail": {
        "error": "InternalServerError",
        "message": "An unexpected error occurred. Please try again.",
        "timestamp": "2026-01-20T10:30:45.123Z"
    }
}
```

---

## Rate Limiting

The API implements rate limiting to protect against abuse:

- **All endpoints**: 20 requests/minute per IP address
- Implemented using `slowapi` middleware
- Returns HTTP 429 (Too Many Requests) when limit exceeded

**Response when rate limit exceeded**:
```json
{
    "error": "Rate limit exceeded: 20 per 1 minute"
}
```

**Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Versioning

API version is included in the URL path:

```
/api/v1/...
```

When breaking changes are introduced, a new version will be created:

```
/api/v2/...
```

Current version: **v1**

---

## Next Steps

- [API Schemas](schemas.md) - Detailed request/response models
- [API Examples](examples.md) - More usage examples
- [Quick Start](../quick-start.md) - Get started quickly

---

**Endpoint Summary**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | System health check |
| `/ask` | POST | Synchronous Q&A |
| `/ask/stream` | POST | Streaming Q&A |
| `/metrics/performance` | GET | Performance metrics |
| `/metrics/usage` | GET | Usage statistics |
| `/metrics/system` | GET | System resources |
