# Quick Start Guide

Get started with the Basecamp Handbook RAG API in under 5 minutes!

## 🚀 Fastest Setup (Docker)

If you have Docker installed, this is the quickest way to get started:

```bash
# 1. Clone and navigate
git clone https://github.com/hanifekaptan/basecamp_handbook_ai_assistant.git
cd basecamp_handbook_ai_assistant

# 2. Start all services
cd docker
docker-compose up -d

# 3. Wait 30 seconds for Ollama to pull the model

# 4. Access the application
# Frontend: http://localhost:8501
# API: http://localhost:8000/docs
```

Done! 🎉

## 💻 Local Development Setup

Prefer running services locally? Follow these steps:

### Step 1: Prerequisites

```bash
# Install Python 3.11+
python --version  # Should be 3.11 or higher

# Install Ollama
# Visit: https://ollama.ai/download

# Verify Ollama installation
ollama --version
```

### Step 2: Pull LLM Model

```bash
# Start Ollama service (keep this terminal open)
ollama serve

# In a new terminal, pull the model (one-time, ~2GB download)
ollama pull llama3.2:3b
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

### Step 4: Frontend Setup

```bash
cd ../frontend

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Run!

```bash
# Terminal 1: Ollama (if not already running)
ollama serve

# Terminal 2: Backend
python backend/main.py

# Terminal 3: Frontend
cd frontend
streamlit run app.py
```

## 🧪 First Test

### Using the Frontend

1. Open http://localhost:8501
2. Type a question: **"What is the vacation policy?"**
3. Click "Ask" or enable streaming
4. View the answer with sources!

### Using the API

```bash
# Check health
curl http://localhost:8000/api/v1/health

# Ask a question
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the vacation policy?"}'
```

## 📊 Verify Setup

Run this checklist:

- [ ] Ollama is running: `curl http://localhost:11434/api/version`
- [ ] Backend is healthy: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend loads: Visit http://localhost:8501
- [ ] Can ask questions in the UI
- [ ] Answers include source citations

## ⚙️ Configuration

### Quick Tweaks

Edit `backend/.env`:

```env
# Use a different model
OLLAMA_MODEL=llama3.2:latest

# Adjust answer creativity (0.0-1.0)
TEMPERATURE=0.3

# Get more context per query
TOP_K_RESULTS=10

# Change server port
PORT=8080
```

Restart the backend after changes.

## 🐛 Common Issues

### "Ollama not available"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not, start it
ollama serve
```

### "No documents indexed"

```bash
# Check if knowledge_base/ has .md files
ls knowledge_base/

# Restart the backend to trigger reindexing
python backend/main.py
```

### Port conflicts

```bash
# Backend (8000)
# Edit backend/.env and change PORT

# Frontend (8501)
# Edit frontend/.streamlit/config.toml
```

### Slow responses

- Ensure Ollama is using GPU acceleration
- Reduce `TOP_K_RESULTS` in `.env`
- Use a smaller model: `llama3.2:3b` (current) is optimized for speed

## 📚 Next Steps

<div class="grid cards" markdown>

-   **Learn the Architecture**

    Understand how the system works

    [Architecture Overview →](architecture/overview.md)

-   **Explore the API**

    See all available endpoints

    [API Reference →](api/endpoints.md)

</div>

## 🎯 Example Questions

Try these questions to explore the system:

| Category | Question |
|----------|----------|
| **Benefits** | "What health insurance options does Basecamp offer?" |
| **Time Off** | "How much vacation time do I get?" |
| **Work Practices** | "What is Basecamp's remote work policy?" |
| **Career** | "How does promotion work at Basecamp?" |
| **Code of Conduct** | "What are the guidelines for workplace behavior?" |

## 💡 Tips

!!! tip "Streaming for Long Answers"
    Enable streaming in the frontend for a better experience with detailed questions.

!!! tip "Prompt Types"
    Try different prompt types:
    - **default**: Balanced answers
    - **friendly**: Conversational tone
    - **concise**: Brief responses

!!! tip "Source Verification"
    Always check the source citations to verify the information.

---

**Need help?** Check the [full documentation](index.md) for more information.
