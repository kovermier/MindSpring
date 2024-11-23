import json
import os
import math
from typing import Optional

# Align chunk size with vector store batch size for efficiency
ITEMS_PER_CHUNK = 100  # Matches ConversationVectorStore batch size
LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB threshold for splitting files

def split_large_json(file_path: str) -> Optional[str]:
    """
    Split a large JSON file into smaller chunks
    
    Args:
        file_path: Path to the JSON file to split
        
    Returns:
        Path to the chunks directory or None if splitting failed
    """
    print(f"Reading {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return None

    # Figure out if it's an array or object
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = list(data.values())  # Use values if it's a dictionary
    else:
        print(f"Error: Data in {file_path} is not a list or dictionary.")
        return None
    
    total_items = len(items)
    total_chunks = math.ceil(total_items / ITEMS_PER_CHUNK)

    print(f"Splitting {total_items} items into {total_chunks} chunks...")

    # Create a directory for the chunks if it doesn't exist
    chunk_dir = f"{file_path.split('.')[0]}_chunks"  # Create directory based on filename
    os.makedirs(chunk_dir, exist_ok=True)

    # Split into chunks with progress tracking
    for i in range(0, total_items, ITEMS_PER_CHUNK):
        chunk = items[i:i + ITEMS_PER_CHUNK]
        
        # Save the chunk
        chunk_file = os.path.join(chunk_dir, f"chunk_{i//ITEMS_PER_CHUNK + 1}.json")
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
        
        # Show progress
        progress = min(100, ((i + ITEMS_PER_CHUNK) * 100) / total_items)
        print(f"Progress: {progress:.1f}% - Saved {chunk_file}")

    return chunk_dir

def should_split_file(file_path: str) -> bool:
    """
    Check if a file should be split based on size threshold
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if file should be split, False otherwise
    """
    try:
        return os.path.getsize(file_path) > LARGE_FILE_THRESHOLD
    except OSError:
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        FILE_TO_SPLIT = sys.argv[1]
        split_large_json(FILE_TO_SPLIT)
    else:
        print("Usage: python split_json.py <filename>")
