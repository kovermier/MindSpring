import json
import os
import pandas as pd
import streamlit as st
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time
from datetime import datetime
import threading
import queue
import ijson
import psutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from split_json import split_large_json, should_split_file, ITEMS_PER_CHUNK
from memlog.conversation_vector_store import ConversationVectorStore

nlp = spacy.load("en_core_web_sm")
analyzer = SentimentIntensityAnalyzer()

# Constants
MAX_RETRIES = 3
BASE_BATCH_SIZE = 100  # Aligned with vector store batch size
MAX_MEMORY_PERCENT = 75
CHECKPOINT_FILE = "conversation_checkpoint.json"
DB_TIMEOUT = 30  # SQLite timeout in seconds
WATCH_DIRECTORIES = ["."]  # Directories to watch for new JSON files

class ConversationFileHandler(FileSystemEventHandler):
    """Handle new conversation JSON files"""
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            print(f"New file detected: {event.src_path}")
            if should_split_file(event.src_path):
                print(f"Large file detected, splitting: {event.src_path}")
                split_large_json(event.src_path)

def start_file_watcher():
    """Start watching directories for new JSON files"""
    observer = Observer()
    handler = ConversationFileHandler()
    
    for directory in WATCH_DIRECTORIES:
        observer.schedule(handler, directory, recursive=False)
    
    observer.start()
    return observer

def load_chunks():
    """Load conversation chunks with improved batch processing"""
    free_gb = check_disk_space()
    if free_gb < 1:
        error_msg = f"⚠️ Low disk space ({free_gb:.2f}GB). Please free up at least 1GB before proceeding."
        print(error_msg)
        return 0

    # Initialize vector store
    try:
        vector_store = ConversationVectorStore(
            model_name="mxbai-embed-large",
            qdrant_path="./qdrant_db",
            collection_name="conversations",
            dimension=1024,
            ollama_url="http://localhost:11434/api/embed"
        )
    except Exception as e:
        print(f"Failed to initialize vector store: {e}")
        return 0

    # Check for large JSON files and split them
    for file in os.listdir():
        if file.endswith('.json') and not file.startswith('chunk_'):
            file_path = os.path.join(os.getcwd(), file)
            if should_split_file(file_path):
                print(f"Large file detected, splitting: {file}")
                split_large_json(file_path)

    chunks_dirs = ["conversations_chunks", "claude_conversations_chunks", "model_comparisons_chunks"]
    total_conversations_loaded = 0
    
    # Process each chunks directory
    for chunks_dir in chunks_dirs:
        if not os.path.exists(chunks_dir):
            continue

        print(f"\nProcessing chunks in {chunks_dir}...")
        chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith('.json')]
        
        for chunk_file in chunk_files:
            try:
                file_path = os.path.join(chunks_dir, chunk_file)
                print(f"Loading {chunk_file}...")
                
                # Load and process chunk
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversations = json.load(f)
                    if isinstance(conversations, list):
                        vector_store.process_conversations(conversations)
                        total_conversations_loaded += len(conversations)
                        print(f"Processed {len(conversations)} conversations from {chunk_file}")
                    else:
                        print(f"Warning: {chunk_file} does not contain a list of conversations")
                        
            except Exception as e:
                print(f"Error processing {chunk_file}: {e}")
                continue
    
    return total_conversations_loaded

def check_disk_space():
    """Check available disk space and return space in GB"""
    try:
        if os.name == 'nt':
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(os.getcwd()), None, None, ctypes.pointer(free_bytes))
            free_gb = free_bytes.value / (1024**3)
            return free_gb
        else:
            st = os.statvfs(os.getcwd())
            free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
            return free_gb
    except Exception as e:
        print(f"Error checking disk space: {e}")
        return 0

def load_all_conversations():
    # Start file watcher
    observer = start_file_watcher()
    try:
        return load_chunks()
    finally:
        # Stop file watcher
        observer.stop()
        observer.join()

if __name__ == "__main__":
    load_all_conversations()
