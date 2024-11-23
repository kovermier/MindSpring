# MindSpring

## Project Overview

MindSpring is a systematic tracking and analysis system for GPT and ClaudeAI conversation JSON exports. It provides tools for processing, visualizing, and analyzing large conversation datasets with a focus on memory efficiency, data privacy, and interactive exploration.

## Key Features

- 🔍 Semantic Search & Analysis
  - Vector-based semantic search
  - Relevance-based filtering
  - Similar conversation discovery
  - Topic modeling and clustering

- 📊 Analysis Tools
  - Conversation pattern analysis
  - Topic distribution insights
  - Interactive topic mindmap
  - Knowledge graph visualization

- 🔒 Privacy & Security
  - Local vector storage with Qdrant
  - Local embedding generation with Ollama
  - PII (Personally Identifiable Information) protection
  - Configurable data exclusion via .gitignore

- 📈 Visualization
  - Streamlit-based interactive UI
  - Knowledge graph with physics-based interactions
  - Clickable nodes for detailed conversation views
  - Similar conversation recommendations

## Project Status

- **Current Phase**: UI Consolidation & Search Enhancement
- **Active Development**: Search Refinement, Knowledge Graph Visualization

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running locally
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
```bash
git clone https://github.com/kovermier/MindSpring.git
cd MindSpring
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Install and start Ollama
- Download and install Ollama from [ollama.ai](https://ollama.ai/)
- Pull the required embedding model:
```bash
ollama pull mxbai-embed-large
```
- Ensure Ollama is running (it should be running as a service)

## Data Preparation

### Conversation JSON File Naming Convention

Ensure your conversation export files follow these naming conventions:

1. **GPT Conversations**:
   - Filename must start with `conversations`
   - Supported formats: 
     - `conversations.json`
     - `conversations_export.json`
     - `conversations_YYYY-MM-DD.json`

2. **Claude Conversations**:
   - Filename must start with `claude_conversations`
   - Supported formats:
     - `claude_conversations.json`
     - `claude_conversations_export.json`
     - `claude_conversations_YYYY-MM-DD.json`

### Data Processing Workflow

1. Place your conversation JSON files in the project root
2. Run the conversation loader (automatically handles file splitting and vector store loading):
```bash
python load_conversations.py
```

## Running the Application

```bash
streamlit run Home.py
```

The application will be available at http://localhost:8501

### Using the Application

1. **Search Conversations**
   - Use the semantic search bar to find relevant conversations
   - Adjust relevance threshold to control match precision
   - View conversation details and similar conversations

2. **Topic Map**
   - Navigate to the Topic Map page to visualize conversation relationships
   - Click nodes to explore related conversations
   - Use the physics-based layout to organize topics

## Project Structure

```
MindSpring/
├── memlog/                    # Project progress tracking
│   ├── conversation_vector_store.py  # Vector store implementation
│   ├── shared_vector_store.py        # Shared vector store instance
│   └── data_flow.md                  # Architecture documentation
├── pages/                     # Streamlit additional pages
│   └── 1_Topic_Map.py         # Topic visualization page
├── conversations_chunks/      # Processed conversation chunks
├── claude_conversations_chunks/  # Claude conversation chunks
├── Home.py                    # Main application interface
├── load_conversations.py      # Conversation data loader
└── requirements.txt          # Project dependencies
```

## Key Components

- `conversation_vector_store.py`: Manages vector embeddings and search using Qdrant
- `load_conversations.py`: Processes conversations and loads them into the vector store
- `Home.py`: Main Streamlit interface with semantic search
- `1_Topic_Map.py`: Interactive topic relationship visualization

## Performance Optimizations

- Batch processing for vector store operations
- Efficient embedding generation with Ollama
- Memory-conscious chunk processing
- Qdrant vector similarity search
- Progress tracking and error handling

## Recent Changes

- **Vector Store Integration**: Successfully integrated Ollama embeddings with Qdrant for semantic search
- **Chunk Processing**: Improved chunk processing with automatic file splitting and progress tracking
- **UI Enhancements**: Added relevance controls and similar conversation recommendations
- **Performance**: Optimized vector store operations and memory usage
- **Error Handling**: Added comprehensive error handling and progress monitoring

## System Architecture

MindSpring utilizes a multi-stage data pipeline:

1. **Data Ingestion:** Raw conversation JSON files are automatically split into manageable chunks
2. **Vector Processing:** 
   - Text extraction from conversations
   - Embedding generation using Ollama
   - Vector storage in Qdrant
3. **Search & Visualization:** 
   - Semantic search using vector similarity
   - Interactive topic visualization
   - Similar conversation discovery

A detailed architecture diagram can be found in `memlog/data_flow.md`.

## Project Progress

See `memlog/memlog.md` for detailed progress tracking and development updates.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License

## Contact

Name: Kurt Overmier
email: kurt@kurtovermier.com
site: smartbrandstrategies.com

## Acknowledgments

- [Ollama](https://ollama.ai/) for local embedding generation
- [Qdrant](https://qdrant.tech/) for vector storage
- [Streamlit](https://streamlit.io/) for the UI framework
- Python Data Science Ecosystem
