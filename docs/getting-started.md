# Getting Started

This guide will help you get the Basecamp Handbook RAG API up and running on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **Python 3.11 or higher** - [Download](https://www.python.org/downloads/)
- **Ollama** - [Download](https://ollama.ai/download)
- **Git** - [Download](https://git-scm.com/downloads)

### Recommended

- **Docker & Docker Compose** - [Download](https://www.docker.com/products/docker-desktop)
- **8GB+ RAM** - For running the LLM model
- **10GB+ free disk space** - For models and vector database

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/hanifekaptan/basecamp_handbook_ai_assistant.git
cd basecamp_handbook_ai_assistant
```

### 2. Install Ollama and Pull Model

```bash
# Start Ollama service
ollama serve

# In a new terminal, pull the model
ollama pull llama3.2:3b
```

!!! tip "GPU Acceleration"
    If you have an NVIDIA GPU, Ollama will automatically use it for faster inference.

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env if needed
```

### 4. Setup Frontend

```bash
cd ../frontend

# Install dependencies
pip install -r requirements.txt
```

### 5. Initialize Data

The system will automatically index the Basecamp Handbook documents on first run. Ensure the `knowledge_base/` directory contains the markdown files.

## Running the Application

### Method 1: Docker Compose (Recommended)

```bash
cd docker
docker-compose up -d
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501
- **Ollama Service**: http://localhost:11434

#### Check Status

```bash
# View logs
docker-compose logs -f

# Check containers
docker-compose ps

# Stop services
docker-compose down
```

### Method 2: Manual Startup

#### Terminal 1: Ollama

```bash
ollama serve
```

#### Terminal 2: Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

#### Terminal 3: Frontend

```bash
cd frontend
streamlit run app.py
```

## Verification

### 1. Check Backend Health

Visit http://localhost:8000/api/v1/health

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "ollama_available": true,
  "documents_indexed": 150
}
```

### 2. Check API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI.

### 3. Check Frontend

Visit http://localhost:8501 to see the Streamlit interface.

## First Question

Try asking:

> "What is Basecamp's vacation policy?"

You should receive an answer with source citations from the handbook.

## Troubleshooting

### Ollama Not Available

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama
ollama serve
```

### No Documents Indexed

Ensure `knowledge_base/` directory has .md files and restart the backend:

```bash
# Restart the backend to trigger reindexing
python backend/main.py
```

### Port Already in Use

Change ports in:
- `backend/.env`: Update `PORT` variable
- `frontend/.streamlit/config.toml`: Update `port` setting
- `docker/docker-compose.yml`: Update port mappings

## Next Steps

- [Architecture Overview](architecture/overview.md) - Understand the system design
- [API Reference](api/endpoints.md) - Explore available endpoints
- [Quick Start Guide](quick-start.md) - Start using the system

## Environment Variables

Key environment variables in `backend/.env`:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# ChromaDB
CHROMA_PERSIST_DIRECTORY=../data/chroma_db

# RAG Settings
CHUNK_SIZE=800
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
TEMPERATURE=0.3

# Logging
LOG_LEVEL=INFO
```

!!! warning "Production Deployment"
    This guide is for local development. For production deployment, see the deployment guide and ensure proper security configurations.
