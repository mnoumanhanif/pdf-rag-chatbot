# Architecture

This document describes the high-level architecture of the PDF RAG Chatbot.

## Overview

The system is a Retrieval-Augmented Generation (RAG) application built with a decoupled architecture. It consists of two main services:

1. **FastAPI Backend** — handles PDF ingestion and query processing
2. **Streamlit Frontend** — provides the chat interface for users

## Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│                  Streamlit UI                     │
│         (app/ui.py — Port 8501)                   │
│                                                   │
│  ┌─────────────┐        ┌──────────────────────┐ │
│  │  PDF Upload  │        │   Chat Interface     │ │
│  └──────┬──────┘        └──────────┬───────────┘ │
└─────────┼──────────────────────────┼─────────────┘
          │ POST /upload             │ POST /query
          ▼                          ▼
┌──────────────────────────────────────────────────┐
│               FastAPI Backend                     │
│          (app/api.py — Port 8000)                 │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │              RAG System                      │ │
│  │            (app/rag.py)                      │ │
│  │                                              │ │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐ │ │
│  │  │PDF Loader│→ │Splitter  │→ │FAISS Store│ │ │
│  │  └──────────┘  └──────────┘  └─────┬─────┘ │ │
│  │                                     │       │ │
│  │  ┌──────────────┐    ┌─────────────▼─────┐ │ │
│  │  │Contextualizer│ →  │  RetrievalQA      │ │ │
│  │  │(History)     │    │  (LLM + Retriever)│ │ │
│  │  └──────────────┘    └───────────────────┘ │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

## Components

### RAG System (`app/rag.py`)

The core logic that powers the chatbot:

- **`RAGSystem` class** — manages the full RAG pipeline
- **`_initialize_llm()`** — selects the LLM provider (Google Gemini or OpenAI) based on available API keys
- **`_load_vector_store()`** — loads any existing FAISS index from disk
- **`ingest_pdfs()`** — loads PDFs, splits them into chunks, and stores embeddings in FAISS
- **`_contextualize_question()`** — reformulates follow-up questions using conversation history into standalone queries
- **`query()`** — runs the full RAG pipeline: contextualize → retrieve → generate

### API Layer (`app/api.py`)

FastAPI endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/upload` | POST | Upload and ingest PDF files |
| `/query` | POST | Query the RAG system with conversation history |

### UI Layer (`app/ui.py`)

Streamlit frontend with:

- Sidebar for PDF file upload
- Chat interface with message history
- Session state management for conversation continuity

## Data Flow

### PDF Ingestion

1. User uploads PDF(s) via Streamlit sidebar
2. Streamlit sends files to `POST /upload`
3. FastAPI saves files temporarily, passes paths to `RAGSystem.ingest_pdfs()`
4. PDFs are loaded with PyPDFLoader, split into chunks (1000 chars, 200 overlap)
5. Chunks are embedded using HuggingFace `all-MiniLM-L6-v2` model
6. Embeddings are stored in FAISS vector store and saved to disk

### Query Processing

1. User asks a question in the chat interface
2. Streamlit sends query + chat history to `POST /query`
3. If chat history exists, the question is reformulated into a standalone query using the Contextualizer chain
4. The standalone question is used to retrieve relevant chunks from FAISS (top 4)
5. Retrieved chunks + question are sent to the LLM
6. The LLM generates an answer, which is returned to the user

## Key Design Decisions

- **FAISS over Chroma/Pinecone** — lightweight, no external service needed, runs on CPU
- **HuggingFace embeddings** — free, no API key required for embeddings
- **Condense Question pattern** — ensures follow-up questions retrieve the correct context
- **Decoupled frontend/backend** — allows independent scaling and deployment
