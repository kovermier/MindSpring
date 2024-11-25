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

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300">
    <!-- Definitions for filters and gradients -->
    <defs>
        <!-- Soft shadow -->
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
            <feOffset dx="2" dy="2" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.2"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

        <!-- Gradient for arrows -->
        <linearGradient id="arrowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#e0e0e0;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#b0b0b0;stop-opacity:1" />
        </linearGradient>

        <!-- Arrow marker -->
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <path d="M0,0 L10,3.5 L0,7" fill="#b0b0b0"/>
        </marker>
    </defs>

    <!-- Nodes -->
    <g transform="translate(50,50)">
        <!-- Raw Conversation Files -->
        <rect x="0" y="0" width="140" height="60" rx="10" fill="#f9f" filter="url(#shadow)"/>
        <text x="70" y="25" text-anchor="middle" fill="#333" font-family="Arial">Raw Conversation</text>
        <text x="70" y="45" text-anchor="middle" fill="#333" font-family="Arial">Files (JSON)</text>

        <!-- load_conversations.py -->
        <rect x="190" y="0" width="140" height="60" rx="10" fill="#fff" filter="url(#shadow)"/>
        <text x="260" y="35" text-anchor="middle" fill="#333" font-family="Arial">load_conversations.py</text>

        <!-- ConversationVectorStore -->
        <rect x="380" y="0" width="140" height="60" rx="10" fill="#fff" filter="url(#shadow)"/>
        <text x="450" y="25" text-anchor="middle" fill="#333" font-family="Arial">Conversation</text>
        <text x="450" y="45" text-anchor="middle" fill="#333" font-family="Arial">VectorStore</text>

        <!-- Ollama API -->
        <rect x="570" y="0" width="140" height="60" rx="10" fill="#fff" filter="url(#shadow)"/>
        <text x="640" y="25" text-anchor="middle" fill="#333" font-family="Arial">Ollama API</text>
        <text x="640" y="45" text-anchor="middle" fill="#333" font-family="Arial">(mxbai-embed-large)</text>

        <!-- Qdrant Vector DB -->
        <rect x="380" y="100" width="140" height="60" rx="10" fill="#bbf" filter="url(#shadow)"/>
        <text x="450" y="135" text-anchor="middle" fill="#333" font-family="Arial">Qdrant Vector DB</text>

        <!-- Home.py -->
        <rect x="190" y="170" width="140" height="60" rx="10" fill="#bfb" filter="url(#shadow)"/>
        <text x="260" y="195" text-anchor="middle" fill="#333" font-family="Arial">Home.py</text>
        <text x="260" y="215" text-anchor="middle" fill="#333" font-family="Arial">(Search Interface)</text>

        <!-- Topic Map -->
        <rect x="570" y="170" width="140" height="60" rx="10" fill="#ccf" filter="url(#shadow)"/>
        <text x="640" y="195" text-anchor="middle" fill="#333" font-family="Arial">Topic_Map.py</text>
        <text x="640" y="215" text-anchor="middle" fill="#333" font-family="Arial">(Visualization)</text>

        <!-- Connecting arrows -->
        <path d="M140,30 L190,30" stroke="url(#arrowGradient)" stroke-width="2" marker-end="url(#arrowhead)"/>
        <path d="M330,30 L380,30" stroke="url(#arrowGradient)" stroke-width="2" marker-end="url(#arrowhead)"/>
        <path d="M520,30 L570,30" stroke="url(#arrowGradient)" stroke-width="2" marker-end="url(#arrowhead)"/>
        <path d="M640,60 L640,80 L450,80 L450,100" stroke="url(#arrowGradient)" stroke-width="2" marker-end="url(#arrowhead)"/>
        <path d="M380,130 L260,130 L260,170" stroke="url(#arrowGradient)" stroke-width="2" marker-end="url(#arrowhead)"/>
        <path d="M520,130 L640,130 L640,170" stroke="url(#arrowGradient)" stroke-width="2" marker-end="url(#arrowhead)"/>
    </g>
</svg>
</div>

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
