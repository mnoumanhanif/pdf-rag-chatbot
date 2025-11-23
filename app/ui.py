import streamlit as st
import requests
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="PDF RAG Chatbot", layout="wide")

st.title("📚 PDF RAG Chatbot")
st.markdown("Upload PDFs and ask questions about their content.")

# Sidebar for File Upload
with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if st.button("Process Documents"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                files = [("files", (file.name, file, "application/pdf")) for file in uploaded_files]
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success(f"Success: {response.json()['message']}")
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to backend. Is it running?")
        else:
            st.warning("Please upload at least one PDF file.")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Prepare chat history (excluding the latest user message which is 'prompt')
            chat_history = st.session_state.messages[:-1]
            response = requests.post(f"{API_URL}/query", json={"query": prompt, "chat_history": chat_history})
            if response.status_code == 200:
                answer = response.json()["answer"]
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = f"Error: {response.text}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to backend. Is it running?"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
