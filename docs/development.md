# Development Guide

This guide covers the development workflow for contributing to the PDF RAG Chatbot.

## Development Setup

### 1. Set Up the Environment

```bash
git clone https://github.com/mnoumanhanif/pdf-rag-chatbot.git
cd pdf-rag-chatbot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your API key(s)
```

### 3. Run in Development Mode

**Backend (with auto-reload):**

```bash
uvicorn app.api:app --reload --port 8000
```

**Frontend:**

```bash
streamlit run app/ui.py
```

## Project Structure

```
pdf-rag-chatbot/
├── app/
│   ├── api.py           # FastAPI endpoints
│   ├── rag.py           # Core RAG logic
│   └── ui.py            # Streamlit frontend
├── docs/                # Project documentation
├── tests/               # Test suite
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
├── CHANGELOG.md         # Version history
├── CONTRIBUTING.md      # Contribution guidelines
├── Dockerfile           # Container configuration
├── LICENSE              # MIT License
├── README.md            # Project overview
└── requirements.txt     # Python dependencies
```

## Code Overview

### `app/rag.py` — RAG System

The `RAGSystem` class manages:

- LLM initialization (Gemini / OpenAI)
- FAISS vector store loading and saving
- PDF ingestion and chunking
- Question contextualization (conversation memory)
- Query execution via RetrievalQA chain

### `app/api.py` — API Layer

Three endpoints:

- `GET /` — health check
- `POST /upload` — accepts PDF files, ingests them into the vector store
- `POST /query` — accepts a query and chat history, returns the RAG answer

### `app/ui.py` — Frontend

Streamlit application with:

- File upload sidebar
- Chat message interface
- Session state for conversation history

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions and classes
- Use the `logging` module instead of `print()`

## Common Development Tasks

### Adding a New LLM Provider

1. Add the provider's LangChain package to `requirements.txt`
2. Add initialization logic in `RAGSystem._initialize_llm()`
3. Set the corresponding environment variable in `.env.example`

### Modifying the Chunking Strategy

Edit the `RecursiveCharacterTextSplitter` parameters in `RAGSystem.ingest_pdfs()`:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # Adjust chunk size
    chunk_overlap=200   # Adjust overlap
)
```

### Adding a New API Endpoint

1. Define request/response models as Pydantic classes in `app/api.py`
2. Add the endpoint function with appropriate decorators
3. Update the Streamlit UI if the endpoint is user-facing
