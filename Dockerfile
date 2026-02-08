# Multi-stage Dockerfile for Basecamp Handbook RAG API
# Optimized for HuggingFace Spaces deployment with Ollama + FastAPI + Streamlit

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    OLLAMA_HOST=127.0.0.1:11434

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    build-essential \
    zstd \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend /app/backend
COPY knowledge_base /app/knowledge_base
COPY frontend /app/frontend
COPY start.sh /app/start.sh

# Make startup script executable
RUN chmod +x /app/start.sh

# Pre-download and verify Ollama model (critical for fast startup)
RUN ollama serve & \
    sleep 10 && \
    ollama pull llama3.2:3b && \
    sleep 5 && \
    pkill ollama

# Create necessary directories
RUN mkdir -p /app/data/chroma_db /app/logs

# Expose Streamlit port (7860 for HF Spaces) and FastAPI port (8000)
EXPOSE 7860 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Start services
CMD ["/app/start.sh"]
