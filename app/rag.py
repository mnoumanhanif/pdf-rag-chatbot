"""Core RAG (Retrieval-Augmented Generation) system for PDF document Q&A."""

import logging
import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_classic.chains import LLMChain, RetrievalQA
from langchain_classic.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

logger = logging.getLogger(__name__)


class RAGSystem:
    """Manages the full RAG pipeline: PDF ingestion, vector storage, and query answering."""

    def __init__(self, vector_store_path: str = "faiss_index"):
        self.vector_store_path = vector_store_path
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.llm = self._initialize_llm()
        self._load_vector_store()

    def _initialize_llm(self):
        """Initialize the LLM provider. Prioritizes Google Gemini, falls back to OpenAI."""
        if os.getenv("GOOGLE_API_KEY"):
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        elif os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        else:
            logger.warning(
                "No API key found for Google or OpenAI. "
                "Chat functionality will not work until keys are set."
            )
            return None

    def _load_vector_store(self):
        """Load an existing FAISS vector store from disk, if available."""
        if os.path.exists(self.vector_store_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
            except Exception as e:
                logger.error("Failed to load vector store: %s", e)
                self.vector_store = None
        else:
            self.vector_store = None

    def ingest_pdfs(self, pdf_paths: List[str]) -> str:
        """Load PDFs, split into chunks, and store embeddings in the vector store."""
        documents = []
        for path in pdf_paths:
            loader = PyPDFLoader(path)
            documents.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(texts, self.embeddings)
        else:
            self.vector_store.add_documents(texts)

        self.vector_store.save_local(self.vector_store_path)
        return f"Processed {len(documents)} pages from {len(pdf_paths)} files."

    def _contextualize_question(self, question: str, chat_history: List[dict]) -> str:
        """Reformulate a follow-up question into a standalone query using chat history."""
        if not chat_history:
            return question

        history_str = ""
        for msg in chat_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"

        template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""

        prompt = PromptTemplate(template=template, input_variables=["chat_history", "question"])
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        return llm_chain.run(chat_history=history_str, question=question)

    def query(self, query_text: str, chat_history: Optional[List[dict]] = None) -> str:
        """Run the full RAG pipeline: contextualize the question, retrieve, and generate an answer."""
        if chat_history is None:
            chat_history = []

        if not self.vector_store:
            return "Vector store is empty. Please upload some documents first."
        if not self.llm:
            return "LLM not initialized. Please check your API keys."

        standalone_question = query_text
        if chat_history:
            try:
                standalone_question = self._contextualize_question(query_text, chat_history)
                logger.info("Contextualized question: %s", standalone_question)
            except Exception as e:
                logger.warning("Failed to contextualize question: %s", e)

        prompt_template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""

        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": prompt},
        )

        result = qa_chain.invoke({"query": standalone_question})
        return result["result"]
