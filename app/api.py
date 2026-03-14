"""FastAPI backend for the PDF RAG Chatbot."""

import logging
import os
import shutil
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.rag import RAGSystem

logger = logging.getLogger(__name__)

app = FastAPI(title="PDF RAG Chatbot API")

rag_system = RAGSystem()


class QueryRequest(BaseModel):
    """Request body for the /query endpoint."""

    query: str
    chat_history: List[dict] = []


class QueryResponse(BaseModel):
    """Response body for the /query endpoint."""

    answer: str


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Welcome to the PDF RAG Chatbot API"}


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and ingest PDF files into the vector store."""
    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are accepted. Got: {file.filename}",
            )

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    saved_paths = []

    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(file_path)

        message = rag_system.ingest_pdfs(saved_paths)

        return {"message": message, "files_processed": [f.filename for f in files]}

    except Exception as e:
        logger.error("Failed to process uploaded files: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for path in saved_paths:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system with an optional chat history for context."""
    try:
        answer = rag_system.query(request.query, request.chat_history)
        return {"answer": answer}
    except Exception as e:
        logger.error("Query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
