import streamlit as st
from memlog.conversation_vector_store import ConversationVectorStore
import os
from pathlib import Path

@st.cache_resource(show_spinner=True)
def get_shared_vector_store():
    """
    Singleton vector store instance shared across all pages.
    Uses Streamlit's cache_resource to ensure only one instance exists.
    """
    with st.spinner("Initializing vector store..."):
        try:
            # Check for stale lock file
            lock_file = Path("./qdrant_db/.lock")
            if lock_file.exists():
                try:
                    os.remove(lock_file)
                except:
                    pass
            
            return ConversationVectorStore(
                model_name="mxbai-embed-large",
                qdrant_path="./qdrant_db",
                collection_name="conversations",
                dimension=1024,  # Correct dimension for mxbai-embed-large
                ollama_url="http://localhost:11434/api/embed"
            )
        except RuntimeError as e:
            st.error(f"Error initializing vector store: {str(e)}")
            return None
