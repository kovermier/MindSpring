import json
from datetime import datetime
from typing import List, Dict, Optional, Generator
from pathlib import Path
import hashlib
import psutil
import time
import threading
import os
import platform
import requests
import numpy as np

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

class ConversationVectorStore:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(
        self,
        model_name: str = "mxbai-embed-large",
        qdrant_path: str = "./qdrant_db",
        collection_name: str = "conversations",
        dimension: int = 1024,  # Correct dimension for mxbai-embed-large
        ollama_url: str = "http://localhost:11434/api/embed"
    ):
        """
        Initialize local vector store with Ollama and Qdrant
        Uses singleton pattern to ensure only one instance exists

        Args:
            model_name: Ollama model to use for embeddings
            qdrant_path: Path to store Qdrant database
            collection_name: Name of the collection in Qdrant
            dimension: Embedding dimension (1024 for mxbai-embed-large)
            ollama_url: Base URL for Ollama API
        """
        # Only initialize once
        if hasattr(self, 'initialized'):
            return
        self.initialized = True

        # Initialize Ollama API parameters
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.ollama_headers = {'Content-Type': 'application/json'}

        # Test Ollama connection
        try:
            self._test_ollama_connection()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Ollama API: {str(e)}")

        # Ensure qdrant directory exists
        os.makedirs(qdrant_path, exist_ok=True)

        # Create lock file path
        self.lock_file = Path(qdrant_path) / ".lock"

        try:
            # Cross-platform file locking
            if platform.system() == 'Windows':
                # Windows-specific handling
                if self.lock_file.exists():
                    try:
                        # Try to open file in exclusive mode
                        self.lock_fd = os.open(str(self.lock_file), os.O_RDWR | os.O_EXCL | os.O_CREAT)
                    except OSError:
                        raise RuntimeError("Another instance is already accessing the vector store")
                else:
                    self.lock_fd = os.open(str(self.lock_file), os.O_RDWR | os.O_CREAT)
            else:
                # Unix-like systems
                import fcntl
                self.lock_fd = os.open(str(self.lock_file), os.O_RDWR | os.O_CREAT)
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Setup Qdrant
            self.client = QdrantClient(path=qdrant_path)
            self.collection_name = collection_name

            # Create collection if it doesn't exist
            self._create_collection(dimension)

            # Track processed conversations
            self.processed_file = Path("processed_conversations.json")
            self.processed_ids = self._load_processed_ids()

            # Performance monitoring
            self.performance_log = Path("vector_store_performance.log")
            self._init_performance_log()

        except Exception as e:
            # Release lock and close file if initialization fails
            self._release_lock()
            raise RuntimeError(f"Error initializing vector store: {str(e)}")

    def _test_ollama_connection(self):
        """Test connection to Ollama API"""
        try:
            # Simple test embedding
            test_payload = {
                "model": self.model_name,
                "input": ["test"]
            }
            response = requests.post(self.ollama_url, headers=self.ollama_headers, json=test_payload, timeout=5)
            response.raise_for_status()
            data = response.json()
            if "embeddings" not in data or not data["embeddings"]:
                raise RuntimeError("Invalid response from Ollama API")
            if len(data["embeddings"][0]) != 1024:
                raise RuntimeError(f"Unexpected embedding dimension: {len(data['embeddings'][0])}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama API: {str(e)}")

    def _release_lock(self):
        """Release file lock in a cross-platform way"""
        try:
            if platform.system() != 'Windows':
                import fcntl
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            os.close(self.lock_fd)
            if self.lock_file.exists():
                os.unlink(str(self.lock_file))
        except:
            pass

    def __del__(self):
        """Cleanup when instance is destroyed"""
        self._release_lock()

    def _init_performance_log(self):
        """Initialize or create performance log file"""
        if not self.performance_log.exists():
            self.performance_log.write_text("timestamp,operation,duration,memory_usage,batch_size\n")

    def _log_performance(self, operation: str, duration: float, batch_size: int = 0):
        """Log performance metrics"""
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp},{operation},{duration:.2f},{memory_usage:.2f},{batch_size}\n"
        
        with open(self.performance_log, 'a') as f:
            f.write(log_entry)

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
        """
        Extract searchable text from conversation
        
        Args:
            conversation: Dictionary containing conversation data
            
        Returns:
            Concatenated string of conversation content
        """
        messages = []
        
        # Handle different conversation formats (GPT vs Claude)
        if "mapping" in conversation:  # GPT format
            for node in conversation.get("mapping", {}).values():
                if node.get("message") and node["message"].get("content"):
                    content = node["message"]["content"].get("parts", [])
                    if content and isinstance(content[0], str):
                        role = node["message"]["author"].get("role", "unknown")
                        messages.append(f"{role}: {content[0]}")
        else:  # Claude format
            for message in conversation.get("messages", []):
                if isinstance(message, dict):
                    role = message.get("role", "unknown")
                    content = message.get("content", "")
                    if content:
                        messages.append(f"{role}: {content}")
        
        title = conversation.get("title", "Untitled Conversation")
        return f"Title: {title}\n\n" + "\n".join(messages)

    def process_conversations(self, conversations: List[dict], batch_size: int = 100):
        """
        Process and store conversations in batches with performance monitoring

        Args:
            conversations: List of conversation dictionaries
            batch_size: Number of conversations to process at once
        """
        start_time = time.time()

        new_conversations = [
            conv for conv in conversations
            if conv.get("id") not in self.processed_ids
        ]

        if not new_conversations:
            print("No new conversations to process")
            return

        total = len(new_conversations)
        print(f"Processing {total} new conversations")

        # Process in batches
        for i in range(0, total, batch_size):
            batch_start = time.time()
            batch = new_conversations[i:i + batch_size]

            # Prepare texts and metadata
            texts = [self._extract_conversation_text(conv) for conv in batch]
            metadata = [
                {
                    "id": conv.get("id", hashlib.md5(str(conv).encode()).hexdigest()),
                    "title": conv.get("title", "Untitled"),
                    "create_time": conv.get("create_time", datetime.now().timestamp()),
                    "update_time": conv.get("update_time", datetime.now().timestamp())
                }
                for conv in batch
            ]

            # Generate embeddings using Ollama API
            try:
                embeddings = self._get_ollama_embeddings(texts)
            except requests.exceptions.RequestException as e:
                self._log_performance("ollama_api_error", time.time() - batch_start, len(batch))
                print(f"Error calling Ollama API: {e}")
                continue # Skip this batch and move to the next

            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=hashlib.md5(str(meta["id"]).encode()).hexdigest(),
                        vector=embedding.tolist(),
                        payload={
                            "text": text,
                            **meta
                        }
                    )
                    for embedding, text, meta
                    in zip(embeddings, texts, metadata)
                ]
            )

            # Update processed IDs
            self.processed_ids.update(meta["id"] for meta in metadata)
            self._save_processed_ids()

            batch_duration = time.time() - batch_start
            self._log_performance("batch_process", batch_duration, len(batch))

            progress = min(100, (i + batch_size) * 100 / total)
            print(f"Progress: {progress:.1f}% ({i + len(batch)}/{total})")

        total_duration = time.time() - start_time
        self._log_performance("total_process", total_duration, total)
        print(f"Processing completed in {total_duration:.2f} seconds")

    def _get_ollama_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using the Ollama API"""
        payload = {
            "model": self.model_name,
            "input": texts
        }
        response = requests.post(self.ollama_url, headers=self.ollama_headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if "embeddings" not in data:
            raise RuntimeError("Invalid response from Ollama API")
        return np.array(data["embeddings"])

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
        start_time = time.time()
        
        # Generate query embedding using Ollama API
        query_vector = self._get_ollama_embeddings([query])[0]
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        
        duration = time.time() - start_time
        self._log_performance("search", duration)
        
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
        search_start = time.time()
        
        query_vector = self._get_ollama_embeddings([query])[0]
        
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
        
        duration = time.time() - search_start
        self._log_performance("filter_search", duration)
        
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

    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {}
