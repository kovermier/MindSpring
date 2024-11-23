import json
from pathlib import Path
from typing import Generator, Dict, Union
from datetime import datetime, timedelta
from conversation_vector_store import ConversationVectorStore

def load_conversation_chunks(chunks_dir: str, batch_size: int = 100) -> Generator[list, None, None]:
    """
    Load conversations from chunked JSON files using a generator to reduce memory usage
    
    Args:
        chunks_dir: Directory containing conversation chunks
        batch_size: Number of conversations to yield at a time
        
    Yields:
        List of conversations up to batch_size
    """
    chunks_path = Path(chunks_dir)
    
    if not chunks_path.exists():
        print(f"Directory not found: {chunks_dir}")
        return
    
    current_batch = []
    
    for chunk_file in chunks_path.glob("chunk_*.json"):
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
                
                # Handle both list and dict formats
                conversations = chunk_data if isinstance(chunk_data, list) else [chunk_data]
                
                for conv in conversations:
                    current_batch.append(conv)
                    
                    if len(current_batch) >= batch_size:
                        yield current_batch
                        current_batch = []
                        
        except Exception as e:
            print(f"Error loading {chunk_file}: {e}")
            continue
    
    # Yield any remaining conversations
    if current_batch:
        yield current_batch

def process_source_conversations(vector_store: ConversationVectorStore, source_dir: str, source_name: str):
    """
    Process conversations from a specific source with progress tracking
    
    Args:
        vector_store: Initialized ConversationVectorStore instance
        source_dir: Directory containing conversation chunks
        source_name: Name of the source (e.g., 'GPT' or 'Claude')
    """
    print(f"\nProcessing {source_name} conversations...")
    
    total_processed = 0
    batch_size = 100
    
    for batch in load_conversation_chunks(source_dir, batch_size):
        vector_store.process_conversations(batch)
        total_processed += len(batch)
        print(f"Progress: {total_processed} conversations processed")
    
    print(f"Completed processing {total_processed} {source_name} conversations")

def demo_search_capabilities(vector_store: ConversationVectorStore):
    """Demonstrate various search capabilities"""
    print("\nSearch Demonstrations:")
    
    # 1. Basic semantic search
    print("\n1. Basic Semantic Search - 'python error handling'")
    results = vector_store.search("capital of France", limit=3)
    display_results(results, "Basic Search")
    
    # 2. Time-filtered search
    print("\n2. Time-filtered Search - 'database optimization' (last month)")
    end_time = datetime.now().timestamp()
    start_time = (datetime.now() - timedelta(days=30)).timestamp()
    
    results = vector_store.filter_search(
        "database optimization",
        start_time=start_time,
        end_time=end_time,
        limit=3
    )
    display_results(results, "Time-filtered Search")

def display_results(results: list, search_type: str):
    """Display search results in a formatted way"""
    if not results:
        print(f"No results found for {search_type}")
        return
        
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Title: {result['title']}")
        print(f"Score: {result['score']:.3f}")
        print(f"Created: {datetime.fromtimestamp(result['create_time']).strftime('%Y-%m-%d %H:%M:%S')}")
        # Show preview of text with context
        preview = result['text'][:200].replace('\n', ' ').strip()
        print(f"Preview: {preview}...")

def main():
    # Initialize vector store
    vector_store = ConversationVectorStore(
        model_name="mxbai-embed-large", # Changed model name
        qdrant_path="./qdrant_db",
        collection_name="conversations"
    )
    
    # Process test conversation
    with open("test_conversation.json", "r") as f:
        test_conversation = json.load(f)
    vector_store.process_conversations([test_conversation])
    
    # Demonstrate search capabilities
    demo_search_capabilities(vector_store)

if __name__ == "__main__":
    main()
