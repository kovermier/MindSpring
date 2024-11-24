# Local Vector Store for Conversations

This project implements a local vector store solution for managing and searching conversations using Langchain, Qdrant, and Sentence Transformers. This approach offers several advantages, including local control over data, efficient processing, and flexible search capabilities.

## Key Features

* **Fully Local Operation:**  Leverages Sentence Transformers for embeddings and Qdrant for vector storage, eliminating external API dependencies.
* **Efficient Processing:** Supports batch processing, tracks processed conversations to avoid duplicates, and handles incremental updates seamlessly.
* **Flexible Search:** Enables semantic similarity search, time-based filtering, and configurable similarity thresholds.
* **Persistence:** Stores all data locally, maintains processing state, and ensures efficient disk usage.
* **Performance:** Provides fast retrieval with Qdrant and efficient embedding generation with Sentence Transformers. Batch processing optimizes performance for large datasets.

## Implementation Details

The core functionality is encapsulated within the `LocalConversationStore` class, which handles embedding generation, vector storage, and search operations.

```python
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import hashlib

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import numpy as np

class LocalConversationStore:
    # ... (class implementation as provided in the original file content)
```

## Usage Example

The following example demonstrates how to initialize the store, process conversations, and perform searches:

```python
# Initialize the store
store = LocalConversationStore()

# Process conversations (your JSON data)
with open('conversations.json', 'r') as f:
    conversations = json.load(f)
store.process_conversations(conversations)

# Search examples
# Simple semantic search
results = store.search("discussions about AI ethics")
for r in results:
    print(f"Title: {r['title']}")
    print(f"Score: {r['score']:.3f}")
    print("---")

# Search with time filter
from datetime import datetime
start_time = datetime(2024, 1, 1).timestamp()
end_time = datetime(2024, 3, 1).timestamp()

filtered_results = store.filter_search(
    "AI project ideas",
    start_time=start_time,
    end_time=end_time
)
```

## Dependencies

This project requires the following libraries:

* `sentence-transformers`
* `qdrant-client`

Ensure these are installed before running the code.  You can install them using pip:

```bash
pip install sentence-transformers qdrant-client
