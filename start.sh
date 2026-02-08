#!/bin/bash
set -e

echo "============================================"
echo "Starting Basecamp Handbook RAG System"
echo "============================================"

# Start Ollama service in background
echo "[1/4] Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "[2/4] Waiting for Ollama to initialize..."
sleep 10

# Verify model is available
echo "[3/4] Verifying llama3.2:3b model..."
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "ERROR: Model not found. Downloading llama3.2:3b..."
    ollama pull llama3.2:3b
fi

# Start FastAPI backend in background
echo "[4/4] Starting FastAPI backend..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 5

# Start Streamlit frontend on port 8501
echo "============================================"
echo "Starting Streamlit UI on port 8501..."
echo "System ready!"
echo "============================================"

# Run Streamlit (this will keep the container running)
streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0

# Cleanup on exit
trap "echo 'Shutting down...'; kill $OLLAMA_PID $BACKEND_PID; exit" SIGTERM SIGINT
