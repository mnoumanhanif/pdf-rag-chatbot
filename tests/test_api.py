"""Tests for the FastAPI endpoints."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def client():
    """Create a test client with a mocked RAG system."""
    mock_rag = MagicMock()

    with patch("app.rag.HuggingFaceEmbeddings"), \
         patch("app.rag.load_dotenv"):
        import importlib

        import app.api

        importlib.reload(app.api)
        app.api.rag_system = mock_rag

        from fastapi.testclient import TestClient

        with TestClient(app.api.app) as tc:
            yield tc, mock_rag


def test_read_root(client):
    """Test the health check endpoint returns a welcome message."""
    test_client, _ = client
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the PDF RAG Chatbot API"}


def test_query_success(client):
    """Test the /query endpoint returns an answer."""
    test_client, mock_rag = client
    mock_rag.query.return_value = "This is a test answer."

    response = test_client.post(
        "/query", json={"query": "What is this about?", "chat_history": []}
    )
    assert response.status_code == 200
    assert response.json() == {"answer": "This is a test answer."}
    mock_rag.query.assert_called_once_with("What is this about?", [])


def test_query_with_history(client):
    """Test the /query endpoint with chat history."""
    test_client, mock_rag = client
    mock_rag.query.return_value = "Follow-up answer."

    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    response = test_client.post(
        "/query", json={"query": "Tell me more", "chat_history": history}
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "Follow-up answer."


def test_query_missing_field(client):
    """Test that /query returns 422 when required field is missing."""
    test_client, _ = client
    response = test_client.post("/query", json={})
    assert response.status_code == 422


def test_upload_rejects_non_pdf(client):
    """Test that /upload rejects non-PDF files."""
    test_client, _ = client
    response = test_client.post(
        "/upload",
        files=[("files", ("test.txt", b"not a pdf", "text/plain"))],
    )
    assert response.status_code == 400
    assert "Only PDF files are accepted" in response.json()["detail"]
