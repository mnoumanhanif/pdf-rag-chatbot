# API Reference

The PDF RAG Chatbot exposes a REST API via FastAPI. When running locally, interactive API docs are available at `http://localhost:8000/docs` (Swagger UI).

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

```
GET /
```

**Response:**

```json
{
  "message": "Welcome to the PDF RAG Chatbot API"
}
```

---

### Upload PDF Files

```
POST /upload
```

Upload one or more PDF files for ingestion into the vector store.

**Request:**

- Content-Type: `multipart/form-data`
- Body: `files` — one or more PDF files

**Example (curl):**

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

**Success Response (200):**

```json
{
  "message": "Processed 15 pages from 2 files.",
  "files_processed": ["document1.pdf", "document2.pdf"]
}
```

**Error Response (500):**

```json
{
  "detail": "Error description"
}
```

---

### Query Documents

```
POST /query
```

Ask a question about the uploaded documents. Supports multi-turn conversation via chat history.

**Request:**

- Content-Type: `application/json`
- Body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The question to ask |
| `chat_history` | array | No | Previous conversation messages |

Each item in `chat_history` should have:

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | `"user"` or `"assistant"` |
| `content` | string | The message content |

**Example (curl):**

```bash
# First question
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of the document?"}'

# Follow-up question with history
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can you explain more about that?",
    "chat_history": [
      {"role": "user", "content": "What is the main topic of the document?"},
      {"role": "assistant", "content": "The document discusses machine learning fundamentals."}
    ]
  }'
```

**Success Response (200):**

```json
{
  "answer": "The document discusses machine learning fundamentals, covering supervised and unsupervised learning approaches."
}
```

**Error Response (500):**

```json
{
  "detail": "Error description"
}
```

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 422 | Validation error (invalid request body) |
| 500 | Internal server error |
