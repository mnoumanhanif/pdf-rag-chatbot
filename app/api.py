import shutil
import os
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.rag import RAGSystem

app = FastAPI(title="PDF RAG Chatbot API")

# Initialize RAG System
# We initialize it globally. In a real prod app, might want dependency injection or singleton pattern.
rag_system = RAGSystem()

class QueryRequest(BaseModel):
    query: str
    chat_history: List[dict] = []

class QueryResponse(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF RAG Chatbot API"}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    saved_paths = []

    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(file_path)
        
        # Process files
        message = rag_system.ingest_pdfs(saved_paths)
        
        # Cleanup temp files
        for path in saved_paths:
            os.remove(path)
        os.rmdir(temp_dir)
        
        return {"message": message, "files_processed": [f.filename for f in files]}
    
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    try:
        answer = rag_system.query(request.query, request.chat_history)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
