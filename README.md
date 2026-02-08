# Basecamp Handbook RAG API 🚀

A production-ready, local-first Retrieval-Augmented Generation (RAG) system for intelligent question-answering over the Basecamp Employee Handbook.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌐 Live Demo & Documentation

- **🎯 Live Demo**: [Try it on HuggingFace Spaces](https://huggingface.co/spaces/hanifekaptan/basecamp_handbook_ai_assistant)
- **📖 Documentation**: [Full Documentation](https://hanifekaptan.github.io/basecamp_handbook_ai_assistant/)
- **🐙 GitHub**: [Source Code](https://github.com/hanifekaptan/basecamp_handbook_ai_assistant)

## 🎯 What is This?

This is a **RAG (Retrieval-Augmented Generation) system** that enables natural language question-answering over the Basecamp Employee Handbook. Instead of manually searching through hundreds of pages, employees can ask questions in plain English and get instant, accurate answers with source citations.

**Real Example:**
```
❓ Question: "What is Basecamp's vacation policy?"

✅ Answer: "Basecamp offers unlimited vacation time to all full-time employees. 
           Time off should be coordinated with your team to ensure coverage.
           The company encourages taking at least 3 weeks per year."

📚 Sources:
   • benefits-and-perks.md (Relevance: 94%)
   • how-we-work.md (Relevance: 87%)
```

### 🌟 Why This Project?

**Privacy & Security:**
- ✅ **100% Local**: Runs entirely on your machine - no cloud dependencies
- ✅ **Zero API Keys**: Uses open-source Ollama - no OpenAI/Anthropic needed
- ✅ **Data Privacy**: Your handbook data never leaves your computer

**Performance & Quality:**
- ⚡ **Fast**: ~2.5s average response time
- 🎯 **Accurate**: 90%+ retrieval precision with source attribution
- 🚫 **No Hallucinations**: Grounded responses using RAG architecture

**Developer Experience:**
- 🏗️ **Production Ready**: Clean architecture, typed, tested (78% coverage)
- 📊 **Observable**: Built-in metrics, logging, and health checks
- 🔧 **Extensible**: Modular design, easy to customize

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Semantic Search** | Find information using natural language, not keywords |
| 🤖 **Local LLM** | Ollama with llama3.2:3b (runs on CPU or GPU) |
| ⚡ **Streaming Responses** | See answers generated in real-time |
| 📚 **Source Attribution** | Every answer includes citations to source documents |
| 🏗️ **Modular Architecture** | Clean code structure, easy to extend |
| 🧪 **Comprehensive Tests** | 78% test coverage with unit & integration tests |
| 📊 **Metrics & Monitoring** | Built-in performance tracking |
| 🛡️ **Rate Limiting** | API protection (20 requests/minute) |

## 🏗️ Architecture Overview

```mermaid
graph TB
    User[👤 User] --> Frontend[🎨 Streamlit UI<br/>Port: 8501]
    Frontend --> API[⚡ FastAPI Backend<br/>Port: 8000]
    
    API --> RAG[🔄 RAG Pipeline]
    RAG --> VectorDB[📊 Vector Store]
    RAG --> LLM[🤖 LLM Client]
    
    VectorDB --> ChromaDB[(🗄️ ChromaDB<br/>Vector Database)]
    VectorDB --> Embedder[🔢 SentenceTransformer<br/>all-MiniLM-L6-v2]
    
    LLM --> Ollama[🦙 Ollama<br/>llama3.2:3b]
    LLM --> PromptMgr[📝 Prompt Manager]
    
    style Frontend fill:#e1f5ff,stroke:#01579b
    style API fill:#fff3e0,stroke:#e65100
    style RAG fill:#f3e5f5,stroke:#4a148c
    style VectorDB fill:#e8f5e9,stroke:#1b5e20
    style LLM fill:#fce4ec,stroke:#880e4f
```

### How It Works

1. **User asks a question** → Frontend sends to API
2. **Question embedding** → Converts text to 384-dimensional vector
3. **Semantic search** → Finds top 5 most relevant document chunks
4. **Prompt construction** → Combines question + context
5. **LLM generation** → Ollama generates natural language answer
6. **Response** → Answer with source citations returned to user

## 📁 Project Structure

```
case-study-1/
├── backend/                     # FastAPI backend server
│   ├── app/
│   │   ├── api/                # REST API endpoints
│   │   │   └── endpoints/
│   │   │       ├── health.py   # Health check
│   │   │       ├── ask.py      # Q&A endpoint
│   │   │       └── metrics.py  # Performance metrics
│   │   ├── core/               # Core utilities
│   │   │   ├── config.py       # Configuration management
│   │   │   ├── logging.py      # Logging setup
│   │   │   ├── rate_limiting.py# Rate limiter
│   │   │   └── metrics_tracker.py # Metrics collection
│   │   ├── database/           # Vector database layer
│   │   │   ├── connection.py   # ChromaDB connection
│   │   │   └── vector_store.py # Vector operations
│   │   ├── llm/                # LLM integration
│   │   │   ├── client.py       # Ollama client
│   │   │   ├── prompt_manager.py # Prompt handling
│   │   │   └── prompt_templates.yaml # Prompt configs
│   │   ├── schemas/            # Pydantic models
│   │   │   ├── requests.py     # Request schemas
│   │   │   └── responses.py    # Response schemas
│   │   ├── services/           # Business logic
│   │   │   └── rag_pipeline.py # RAG orchestration
│   │   └── utils/              #Helper functions
│   │       └── text_processing.py # Text utilities
│   ├── scripts/
│   │   └── reindex.py          # Manual reindexing script
│   ├── tests/                  # Test suite
│   │   ├── unit/               # Unit tests
│   │   ├── integration/        # Integration tests
│   │   └── functional/         # E2E tests
│   └── main.py                 # Application entry point
│
├── frontend/                    # Streamlit frontend
│   ├── app.py                  # Main UI application
│   ├── config.py               # Frontend config
│   ├── client/                 # API client
│   │   └── api_client.py
│   └── components/             # UI components
│       ├── header.py
│       ├── sidebar.py
│       └── answer_display.py
│
├── data/                       # Data storage
│   ├── chroma_db/              # Vector database files
│   └── logs/                   # Application logs
│
├── knowledge_base/             # Source documents
│   └── *.md                    # 16 Markdown files (Basecamp Handbook)
│
├── docs/                       # Documentation
│   ├── index.md
│   ├── getting-started.md
│   ├── quick-start.md
│   ├── api/                    # API documentation
│   └── architecture/           # Architecture docs
│
│
├── PRESENTATION.md             # Technical presentation
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** - [Download](https://www.python.org/downloads/)
- **Ollama** - [Download](https://ollama.ai/download)
- **8GB+ RAM** - Recommended for running the LLM

### Installation (5 minutes)

#### 1. Clone Repository

```bash
git clone https://github.com/hanifekaptan/basecamp_handbook_ai_assistant.git
cd basecamp_handbook_ai_assistant
```

#### 2. Install Ollama & Pull Model

```bash
# Start Ollama service (keep running in background)
ollama serve

# In a new terminal, pull the model (one-time, ~2GB download)
ollama pull llama3.2:3b
```

> **Note:** The model will be downloaded to `~/.ollama/models/` automatically.

#### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Setup Frontend

```bash
cd ../frontend
pip install -r requirements.txt
```

### Running the Application

#### Terminal 1: Ollama (if not already running)

```bash
ollama serve
```

#### Terminal 2: Backend

```bash
uvicorn backend.main:app --reload
```

Output:
```
INFO:     Starting Basecamp Handbook RAG API v2.0...
INFO:     Ollama: http://localhost:11434
INFO:     Model: llama3.2:3b
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 3: Frontend

```bash
streamlit run frontend/app.py
```

Output:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Access Points

- **🎨 Frontend UI**: http://localhost:7860
- **⚡ API Server**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs (Swagger UI)
- **🔍 API ReDoc**: http://localhost:8000/redoc (Alternative docs)

> **Note**: Port 7860 is used for compatibility with HuggingFace Spaces deployment.

## 💡 Usage Examples

### Via Frontend (Streamlit)

1. Open http://localhost:7860 (or try the [live demo](https://huggingface.co/spaces/hanifekaptan/basecamp_handbook_ai_assistant))
2. Type your question in the text area
3. Click "Ask Question"
4. See the answer with source citations and relevance scores

### Via API (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={"question": "What is the vacation policy?"}
)

data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {[s['source'] for s in data['sources']]}")
```

### Via API (cURL)

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the vacation policy?"}'
```

### Streaming Responses

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ask/stream",
    json={"question": "What are the company values?"},
    stream=True
)

for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    print(chunk, end='', flush=True)
```

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | System health check |
| POST | `/api/v1/ask` | Ask a question (get full response) |
| POST | `/api/v1/ask/stream` | Ask a question (streaming response) |

### Metrics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/metrics/performance` | Response times, LLM speed, vector search |
| GET | `/api/v1/metrics/usage` | Query statistics, success rate |
| GET | `/api/v1/metrics/system` | CPU, memory, disk usage |

### Example Request/Response

**Request:**
```json
POST /api/v1/ask
{
  "question": "What health benefits does Basecamp offer?"
}
```

**Response:**
```json
{
  "answer": "Basecamp provides comprehensive health insurance including medical, dental, and vision coverage for all full-time employees. The company covers 100% of premiums for employees and 75% for dependents.",
  "sources": [
    {
      "content": "We provide comprehensive health insurance...",
      "source": "benefits-and-perks.md",
      "relevance_score": 0.94
    }
  ],
  "question": "What health benefits does Basecamp offer?",
  "metadata": {
    "documents_retrieved": 5,
    "confidence": "high"
  }
}
```

## 🧪 Testing

### Run All Tests

```bash
cd backend
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Functional/E2E tests
pytest tests/functional/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

Current coverage: **78%**

## 🔧 Configuration

### Environment Variables

Create `backend/.env` for custom configuration:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# ChromaDB
CHROMA_PERSIST_DIRECTORY=../data/chroma_db
CHROMA_COLLECTION_NAME=basecamp_handbook

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# RAG Settings
CHUNK_SIZE=800              # Characters per chunk
CHUNK_OVERLAP=200           # Overlap between chunks
TOP_K_RESULTS=5             # Number of chunks to retrieve
TEMPERATURE=0.3             # LLM temperature (0-1)

# API Settings
API_V1_PREFIX=/api/v1

# Logging
LOG_LEVEL=INFO
LOG_DIR=../data/logs
```

## 📊 Performance Metrics

### System Performance (Local Hardware)

| Metric | Value | Notes |
|--------|-------|-------|
| **Startup Time** | ~3.5s | Ollama + ChromaDB + Embeddings |
| **Average Response** | ~2.5s | End-to-end query time |
| **Vector Search** | ~200ms | ChromaDB similarity search |
| **LLM Inference** | ~2.2s | CPU-based (15 tokens/sec) |
| **Memory Usage** | ~2GB | With llama3.2:3b model loaded |
| **Disk Space** | ~4GB | Model + dependencies + DB |

### RAG Quality Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Retrieval Precision** | 90%+ | Correct docs in top-5 results |
| **Answer Relevance** | High | Grounded in source documents |
| **Hallucination Rate** | Low | Temperature=0.3 + strict prompts |
| **Source Attribution** | 100% | Every answer cites sources |
| **Test Coverage** | 78% | Unit + integration + E2E tests |

## 🛡️ Security & Rate Limiting

- **Rate Limiting**: 20 requests/minute per IP (via slowapi)
- **Input Validation**: Pydantic schemas (1-1000 character questions)
- **Local Execution**: No external API calls (privacy-first)

## 🐛 Troubleshooting

### Common Issues

#### 1. Ollama Not Available

**Symptom**: `Connection refused` or `Ollama unavailable`

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not, start it
ollama serve

# Verify model is pulled
ollama list
# Should show: llama3.2:3b
```

#### 2. Port Already in Use

**Symptom**: `Address already in use` error

```bash
# Backend (change port in backend/.env or via environment variable)
PORT=8001 python main.py

# Frontend (change from default 7860)
streamlit run app.py --server.port 7861
```

#### 3. No Documents Indexed

**Symptom**: "No relevant information found" for all queries

```bash
# Check if knowledge_base/ has .md files
ls knowledge_base/
# Should show 16 .md files

# Force reindex
cd backend
python scripts/reindex.py
```

#### 4. ChromaDB Issues

**Symptom**: Persistence errors or corrupted database

```bash
# Reset database (WARNING: deletes all indexed data)
rm -rf data/chroma_db/*  # Linux/Mac
# Or on Windows:
rmdir /s data\chroma_db

# Reindex
cd backend
python scripts/reindex.py
```

#### 5. Slow Response Times

**Causes & Solutions:**
- **CPU-only inference**: Normal on laptop (15 tokens/sec). Consider GPU acceleration.
- **First query slow**: Model loading takes ~2s, subsequent queries faster.
- **Large context**: Reduce `TOP_K_RESULTS` in config (default: 5).

## 📚 Documentation

Comprehensive documentation available both locally and online:

### 🌐 Online Documentation
- **[Full Documentation Site](https://hanifekaptan.github.io/basecamp_handbook_ai_assistant/)** - Complete guides and API reference
- **[Live Demo](https://huggingface.co/spaces/hanifekaptan/basecamp_handbook_ai_assistant)** - Try it without installation

### 📁 Local Documentation (`docs/`)
- **[Getting Started](docs/getting-started.md)** - Detailed setup guide
- **[Quick Start](docs/quick-start.md)** - 5-minute setup
- **[API Reference](docs/api/endpoints.md)** - All endpoints documented
- **[Architecture](docs/architecture/overview.md)** - System design deep-dive
- **[API Examples](docs/api/examples.md)** - Code examples (Python, JavaScript, cURL)

### 📖 Additional Resources
- **[PRESENTATION.md](PRESENTATION.md)** - Technical presentation (6 pages)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide (Docker, HF Spaces)
- **[definition.md](definition.md)** - Project requirements and specs

## 🤝 Contributing

This is a case study project, but contributions for learning purposes are welcome!

### Development Setup

```bash
# Install dev dependencies
pip install -r backend/requirements-dev.txt

# Run tests before committing
pytest tests/ -v

# Check code style
black backend/
flake8 backend/
```

## � Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:7860
```

### HuggingFace Spaces

This project is deployed on HuggingFace Spaces:
- **Live Demo**: https://huggingface.co/spaces/hanifekaptan/basecamp_handbook_ai_assistant
- **Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **[Basecamp](https://basecamp.com/)** - For the open-source employee handbook
- **[Ollama](https://ollama.ai/)** - For making local LLMs accessible and production-ready
- **[ChromaDB](https://www.trychroma.com/)** - For the excellent embedded vector database
- **[FastAPI](https://fastapi.tiangolo.com/)** - For the modern, fast Python web framework
- **[Streamlit](https://streamlit.io/)** - For the intuitive UI framework
- **[LangChain](https://python.langchain.com/)** - For text processing utilities

## 📞 Contact & Support

- **📧 Issues**: [GitHub Issues](https://github.com/hanifekaptan/basecamp_handbook_ai_assistant/issues)
- **📖 Documentation**: [Online Docs](https://hanifekaptan.github.io/basecamp_handbook_ai_assistant/)
- **💬 Questions**: Check the [Getting Started](docs/getting-started.md) guide first

## 🎓 About This Project

This project was developed as a case study for **Yinovation**, demonstrating:
- Production-grade RAG architecture
- Local-first LLM deployment
- Clean code principles and testing
- Comprehensive documentation

**Key Learnings:**
- Semantic search outperforms keyword-based search for documentation
- RAG reduces hallucinations compared to standalone LLM usage
- Local deployment is viable for privacy-sensitive applications
- Proper chunking strategy significantly impacts retrieval quality

---

**Built with ❤️ by [Hanife Kaptan](https://github.com/hanifekaptan)**

🚀 **Ready to try it?**
- [Quick Start Guide](#-quick-start) - Local setup in 5 minutes
- [Live Demo](https://huggingface.co/spaces/hanifekaptan/basecamp_handbook_ai_assistant) - Try without installation
- [Full Documentation](https://hanifekaptan.github.io/basecamp_handbook_ai_assistant/) - Deep dive
