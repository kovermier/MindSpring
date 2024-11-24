# Local Vector Store Project

Let's build a solution using all local components with Langchain, Qdrant (for vector store), and Sentence Transformers for embeddings. This keeps everything local and efficient.
pythonCopyimport json
```py
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
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        qdrant_path: str = "./qdrant_db",
        collection_name: str = "conversations",
        dimension: int = 384  # Default for MiniLM
    ):
        """
        Initialize local vector store with SentenceTransformers and Qdrant
        
        Args:
            model_name: SentenceTransformer model to use
            qdrant_path: Path to store Qdrant database
            collection_name: Name of the collection in Qdrant
            dimension: Embedding dimension (384 for MiniLM)
        """
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(model_name)
        
        # Setup Qdrant
        self.client = QdrantClient(path=qdrant_path)
        self.collection_name = collection_name
        
        # Create collection if it doesn't exist
        self._create_collection(dimension)
        
        # Track processed conversations
        self.processed_file = Path("processed_conversations.json")
        self.processed_ids = self._load_processed_ids()

    def _create_collection(self, dimension: int):
        """Create Qdrant collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )

    def _load_processed_ids(self) -> set:
        """Load set of processed conversation IDs"""
        if self.processed_file.exists():
            return set(json.loads(self.processed_file.read_text()))
        return set()

    def _save_processed_ids(self):
        """Save processed conversation IDs"""
        self.processed_file.write_text(json.dumps(list(self.processed_ids)))

    def _extract_conversation_text(self, conversation: dict) -> str:
        """Extract searchable text from conversation"""
        messages = []
        for node in conversation.get("mapping", {}).values():
            if node.get("message") and node["message"].get("content"):
                content = node["message"]["content"].get("parts", [])
                if content and isinstance(content[0], str):
                    role = node["message"]["author"].get("role", "unknown")
                    messages.append(f"{role}: {content[0]}")
        
        return f"Title: {conversation.get('title', '')}\n\n" + "\n".join(messages)

    def process_conversations(self, conversations: List[dict], batch_size: int = 100):
        """
        Process and store conversations in batches
        
        Args:
            conversations: List of conversation dictionaries
            batch_size: Number of conversations to process at once
        """
        new_conversations = [
            conv for conv in conversations 
            if conv["id"] not in self.processed_ids
        ]
        
        if not new_conversations:
            print("No new conversations to process")
            return

        print(f"Processing {len(new_conversations)} new conversations")

        # Process in batches
        for i in range(0, len(new_conversations), batch_size):
            batch = new_conversations[i:i + batch_size]
            
            # Prepare texts and metadata
            texts = [self._extract_conversation_text(conv) for conv in batch]
            metadata = [
                {
                    "id": conv["id"],
                    "title": conv["title"],
                    "create_time": conv["create_time"],
                    "update_time": conv["update_time"]
                }
                for conv in batch
            ]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts)
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=hashlib.md5(conv["id"].encode()).hexdigest(),
                        vector=embedding.tolist(),
                        payload={
                            "text": text,
                            **meta
                        }
                    )
                    for conv, embedding, text, meta 
                    in zip(batch, embeddings, texts, metadata)
                ]
            )
            
            # Update processed IDs
            self.processed_ids.update(conv["id"] for conv in batch)
            self._save_processed_ids()
            
            print(f"Processed batch of {len(batch)} conversations")

    def search(
        self, 
        query: str, 
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search conversations by semantic similarity
        
        Args:
            query: Search query
            limit: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of matching conversations with scores
        """
        # Generate query embedding
        query_vector = self.embedding_model.encode(query)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return [
            {
                "id": point.payload["id"],
                "title": point.payload["title"],
                "text": point.payload["text"],
                "create_time": point.payload["create_time"],
                "score": point.score
            }
            for point in results
        ]

    def filter_search(
        self,
        query: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search conversations with time filters
        
        Args:
            query: Search query
            start_time: Start timestamp
            end_time: End timestamp
            limit: Number of results
            
        Returns:
            Filtered and ranked conversations
        """
        query_vector = self.embedding_model.encode(query)
        
        # Build filter conditions
        filter_conditions = []
        if start_time is not None:
            filter_conditions.append(
                models.FieldCondition(
                    key="create_time",
                    range=models.Range(gte=start_time)
                )
            )
        if end_time is not None:
            filter_conditions.append(
                models.FieldCondition(
                    key="create_time",
                    range=models.Range(lte=end_time)
                )
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=models.Filter(
                must=filter_conditions
            ) if filter_conditions else None
        )
        
        return [
            {
                "id": point.payload["id"],
                "title": point.payload["title"],
                "text": point.payload["text"],
                "create_time": point.payload["create_time"],
                "score": point.score
            }
            for point in results
        ]
```
Usage example:
pythonCopy# Initialize the store
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
Key features of this local solution:

Fully Local Operation:

SentenceTransformers for embeddings
Qdrant for vector storage
No external API dependencies


Efficient Processing:

Batch processing support
Tracks processed conversations to avoid duplicates
Handles incremental updates


Flexible Search:

Semantic similarity search
Time-based filtering
Configurable similarity thresholds


Persistence:

All data stored locally
Maintains processing state
Efficient disk usage


Performance:

Fast retrieval with Qdrant
Efficient embedding with SentenceTransformers
Batch processing for large datasets



This solution gives you complete control over your data and processing pipeline while maintaining good performance. You can easily modify the embedding model or vector store configuration based on your specific needs.
