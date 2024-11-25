# Conversation Mind Data Flow Architecture

## Overview

This document outlines the data flow architecture of the MindSpring system, showing how data moves from raw conversation files through processing to searchable vector embeddings.

## Core Components

### 1. Data Storage Layer

- **Qdrant Vector Store** (`./qdrant_db`)
    - Stores conversation embeddings.
    - Enables semantic search.
    - Manages vector indices.

### 2. Processing Components

- **`load_conversations.py`**
    - Handles file watching, splitting, and loading.
    - Manages batch processing of conversations.
    - Implements retry logic and progress tracking.

- **`ConversationVectorStore` (`memlog/conversation_vector_store.py`)**
    - Generates embeddings using Ollama's `mxbai-embed-large` model.
    - Manages Qdrant interactions (upserting and searching).
    - Provides search capabilities.
    - Implements singleton pattern via `shared_vector_store.py`.

### 3. Shared Resources

- **Vector Store Singleton** (`memlog/shared_vector_store.py`)
    - Ensures a single instance of `ConversationVectorStore` across pages.
    - Handles lock file management for thread safety.

## Data Flow Sequence

[Data Flow Diagram](memlog/data_flow.svg)

## Processing Pipeline

1. **Data Loading and Processing:**

   - `load_conversations.py` watches for new conversation files.
   - Files are split into chunks if they exceed a size limit.
   - Chunks are loaded and processed in batches by `load_conversations.py`.
   - `ConversationVectorStore` is used to generate embeddings and store them in Qdrant.

2. **Vector Processing:**

   - `ConversationVectorStore` extracts text from conversation chunks.
   - Embeddings are generated using the Ollama API with the `mxbai-embed-large` model.
   - Vectors and metadata are upserted into the Qdrant database.

3. **Search Flow:**

   - User enters a query in `Home.py`.
   - `ConversationVectorStore` generates an embedding for the query using Ollama.
   - Qdrant performs a similarity search based on the query embedding.
   - Results are returned to `Home.py` and displayed.

4. **Visualization:**
    - `pages/1_Topic_Map.py` uses the shared `ConversationVectorStore` to access embeddings and metadata for visualization.


## Performance Considerations

- **Memory Management:** Adaptive batch sizing based on available memory.
- **Error Handling:** Retries with exponential backoff, checkpointing for recovery.
- **Resource Optimization:** Singleton pattern for shared resources, caching.

## Monitoring and Logging

- **Progress Tracking:** Chunk processing status, success/failure rates.
- **Error Logging:** Detailed error messages and retry attempts.

## Security Measures

- File Access: Lock file management for thread safety.


## Integration Points

- **Web Interface:** Streamlit-based UI for search and visualization.
- **Vector Store Integration:** Shared `ConversationVectorStore` instance.
