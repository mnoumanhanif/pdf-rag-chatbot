"""Tests for the RAG system module."""

from unittest.mock import MagicMock, patch

from app.rag import RAGSystem


@patch("app.rag.HuggingFaceEmbeddings")
@patch("app.rag.load_dotenv")
def test_initialize_llm_no_keys(mock_dotenv, mock_embeddings):
    """Test that LLM is None when no API keys are set."""
    with patch.dict("os.environ", {}, clear=True):
        rag = RAGSystem.__new__(RAGSystem)
        rag.embeddings = MagicMock()
        rag.vector_store = None
        rag.vector_store_path = "faiss_index"
        llm = rag._initialize_llm()
        assert llm is None


@patch("app.rag.HuggingFaceEmbeddings")
@patch("app.rag.load_dotenv")
def test_query_no_vector_store(mock_dotenv, mock_embeddings):
    """Test that query returns a message when vector store is empty."""
    rag = RAGSystem.__new__(RAGSystem)
    rag.vector_store = None
    rag.llm = MagicMock()
    result = rag.query("test question")
    assert "upload some documents" in result.lower()


@patch("app.rag.HuggingFaceEmbeddings")
@patch("app.rag.load_dotenv")
def test_query_no_llm(mock_dotenv, mock_embeddings):
    """Test that query returns a message when LLM is not initialized."""
    rag = RAGSystem.__new__(RAGSystem)
    rag.vector_store = MagicMock()
    rag.llm = None
    result = rag.query("test question")
    assert "api keys" in result.lower()


@patch("app.rag.HuggingFaceEmbeddings")
@patch("app.rag.load_dotenv")
def test_query_default_chat_history_is_none(mock_dotenv, mock_embeddings):
    """Test that the default chat_history is None (not a mutable default)."""
    import inspect

    sig = inspect.signature(RAGSystem.query)
    default = sig.parameters["chat_history"].default
    assert default is None


@patch("app.rag.HuggingFaceEmbeddings")
@patch("app.rag.load_dotenv")
def test_contextualize_question_empty_history(mock_dotenv, mock_embeddings):
    """Test that contextualize returns the original question when history is empty."""
    rag = RAGSystem.__new__(RAGSystem)
    rag.llm = MagicMock()
    result = rag._contextualize_question("What is this?", [])
    assert result == "What is this?"
