# Setup Guide

This guide covers how to install and configure the PDF RAG Chatbot.

## Prerequisites

- **Python 3.9+**
- **pip** package manager
- An API key for **Google Gemini** or **OpenAI**

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mnoumanhanif/pdf-rag-chatbot.git
cd pdf-rag-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

The system prioritizes Google Gemini. If no Google API key is found, it falls back to OpenAI.

## Running the Application

You need two terminals — one for the backend and one for the frontend.

**Terminal 1 — Backend (FastAPI):**

```bash
uvicorn app.api:app --reload --port 8000
```

**Terminal 2 — Frontend (Streamlit):**

```bash
streamlit run app/ui.py
```

The Streamlit UI will open at `http://localhost:8501` and connects to the FastAPI backend at `http://localhost:8000`.

## Docker Setup

Build and run using Docker:

```bash
docker build -t pdf-rag-chatbot .
docker run -p 8000:8000 -p 8501:8501 --env-file .env pdf-rag-chatbot
```

## Verifying the Installation

1. Open the Streamlit UI at `http://localhost:8501`
2. Upload a PDF using the sidebar
3. Ask a question about the uploaded document
4. The system should return an answer based on the document content
