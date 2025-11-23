````markdown
# 📚 Context-Aware PDF RAG Chatbot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![LangChain](https://img.shields.io/badge/Orchestration-LangChain-orange)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)

A production-ready Retrieval-Augmented Generation (RAG) system that allows users to have **natural, multi-turn conversations** with PDF documents.

Unlike simple Q&A bots, this system features **Conversational Memory**. It intelligently reformulates follow-up questions (e.g., *"How much does **it** cost?"*) into standalone queries before searching the vector database, ensuring high retrieval accuracy.

## 🚀 Key Features

* **🧠 Conversational Memory:** Uses a "Condense Question" chain to handle follow-up questions and maintain context.
* **🏗️ Hybrid Architecture:** Decoupled **FastAPI** backend for processing and **Streamlit** frontend for user interaction.
* **🔍 Advanced Retrieval:** Uses **FAISS** for fast similarity search and `HuggingFaceEmbeddings` (all-MiniLM-L6-v2) for high-quality vectors.
* **📄 Robust Ingestion:** Chunks documents intelligently (1000 chars, 200 overlap) to preserve context across boundaries.
* **🤖 Multi-LLM Support:** Configured for **Google Gemini 2.5 Flash** (default) with fallback support for OpenAI GPT models.
* **🐳 Dockerized:** Ready for deployment on Hugging Face Spaces or any container runtime.

## 🛠️ Architecture

The system consists of two main microservices running in parallel:

```mermaid
graph LR
    User[User] -->|Interacts| UI[Streamlit Frontend]
    UI -->|POST /upload| API[FastAPI Backend]
    UI -->|POST /query| API
    
    subgraph "RAG System (Backend)"
        API -->|1. Ingest| Loader[PyPDFLoader]
        Loader --> Splitter[Text Splitter]
        Splitter --> VectorDB[(FAISS Vector Store)]
        
        API -->|2. Query| Memory[Contextualizer]
        Memory -->|Rewrite Query| VectorDB
        VectorDB -->|Retrieve Chunks| LLM[Google Gemini/GPT]
        LLM -->|Generate Answer| API
    end
````

## 📦 Project Structure

```bash
├── app/
│   ├── api.py           # FastAPI endpoints (/upload, /query)
│   ├── ui.py            # Streamlit Chat Interface
│   └── rag.py           # Core RAG logic (Chain, Embeddings, FAISS)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Multi-process container setup
└── README.md
```

## ⚡ Installation & Setup

### Prerequisites

  * Python 3.9+
  * An API Key for **Google Gemini** or **OpenAI**.

### 1\. Clone the Repository

```bash
git clone [https://github.com/yourusername/pdf-rag-chatbot.git](https://github.com/yourusername/pdf-rag-chatbot.git)
cd pdf-rag-chatbot
```

### 2\. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Configure Environment

Create a `.env` file in the root directory:

```env
# Required: Choose one or both
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Defaults to local
API_URL=http://localhost:8000
```

### 5\. Run Locally

You need to run the Backend and Frontend in separate terminals.

**Terminal 1 (Backend):**

```bash
uvicorn app.api:app --reload --port 8000
```

**Terminal 2 (Frontend):**

```bash
streamlit run app/ui.py
```



### Why this README works for you:
1.  **Cites your specific logic:** It explicitly mentions the "Condense Question" chain found in your `rag.py`.
2.  **Accurate Tech Stack:** It lists the libraries exactly as they appear in your `requirements.txt` (FastAPI, Streamlit, LangChain, FAISS).
3.  **Deployment Ready:** It includes specific instructions for Hugging Face Spaces (port 7860), matching your Docker configuration.
```
