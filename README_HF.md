---
title: Basecamp Handbook RAG
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# 📚 Basecamp Employee Handbook - RAG System

Ask questions about the Basecamp employee handbook powered by:
- **LLM:** Llama 3.2 3B (via Ollama) 
- **Vector DB:** ChromaDB with semantic search
- **Embeddings:** all-MiniLM-L6-v2

## 🚀 Features

- ✅ **Local LLM** - No external API costs
- ✅ **Semantic Search** - Find relevant information contextually  
- ✅ **Source Attribution** - Every answer includes source documents
- ✅ **Grounded Answers** - Prevents hallucinations
- ✅ **Streaming Support** - Real-time response generation

## 🏗️ Architecture

```
Streamlit UI (Port 8501) 
    ↓
FastAPI Backend (Port 8000)
    ↓
Ollama LLM (Port 11434) + ChromaDB
```

## 📖 Usage

Simply type your question about Basecamp's employee policies and get accurate, source-backed answers!

Example questions:
- "What is the vacation policy?"
- "Tell me about employee benefits"
- "How does remote work function?"

## 🔧 Tech Stack

- **Backend:** FastAPI + Python 3.11
- **LLM:** Ollama (llama3.2:3b)
- **Vector DB:** ChromaDB
- **Embeddings:** sentence-transformers
- **Frontend:** Streamlit
- **Deployment:** Docker on HuggingFace Spaces

## ⚡ Performance

- **First Request:** ~30 seconds (model loading)
- **Subsequent:** ~3-5 seconds per query
- **Documents Indexed:** 200+ chunks from Basecamp handbook

## 📝 Note

This is a case study project demonstrating RAG (Retrieval-Augmented Generation) implementation with local LLMs.

---

Built with ❤️ for the Yinovation case study.
