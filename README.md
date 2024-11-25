# Project Memlog - MindSpring

## Overview
**Project**: MindSpring
**Start Date**: 2024-11-19
**Status**: Active
**Lead**: Kurt Overmier

## Quick Links
- Repository: https://github.com/kovermier/MindSpring.git
- Docs: (Not yet available)
- Boards: (Not yet available)
- Chat: (Not yet available)

## Status Legend
- 🟢 On Track
- 🟡 At Risk
- 🔴 Blocked
- ⭐ Milestone
- 📝 Needs Review

## Daily Logs
(See memlog/memlog.md for detailed daily logs)


## Tasks

### Active
| ID | Task | Status | Owner | Due |
|----|------|--------|-------|-----|
| 001 | Implement advanced topic analysis | 🟢 | Kover | - |
| 002 | Add usage statistics dashboard | 🟢 | Kover | - |
| 003 | Enhance knowledge graph visualization | 🟢 | Kover | - |

### Completed
(See memlog/memlog.md for completed tasks)


## AI Assistant Sessions


## Code Snippets

## Project Description
MindSpring is a systematic tracking and analysis system for GPT and ClaudeAI conversation JSON exports. It provides tools for processing, visualizing, and analyzing large conversation datasets with a focus on memory efficiency, data privacy, and interactive exploration.

## Key Features
- Semantic Search & Analysis: Vector-based semantic search, relevance-based filtering, similar conversation discovery, topic modeling and clustering.
- Analysis Tools: Conversation pattern analysis, topic distribution insights, interactive topic mindmap, knowledge graph visualization.
- Privacy & Security: Local vector storage with Qdrant, local embedding generation with Ollama, PII protection, configurable data exclusion.
- Visualization: Streamlit-based interactive UI, knowledge graph with physics-based interactions, clickable nodes, similar conversation recommendations.

## Prerequisites
- Python 3.8+
- Ollama installed and running locally
- Dependencies listed in `requirements.txt`

## Installation
1. Clone the repository: `git clone https://github.com/kovermier/MindSpring.git && cd MindSpring`
2. Create a virtual environment: `python -m venv venv && source venv/bin/activate` (On Windows: `venv\Scripts\activate`)
3. Install dependencies: `pip install -r requirements.txt`
4. Install and start Ollama: Download from ollama.ai, pull the `mxbai-embed-large` model, ensure Ollama is running.

## Data Preparation
### Conversation JSON File Naming Convention
- GPT: `conversations.json`, `conversations_export.json`, `conversations_YYYY-MM-DD.json`
- Claude: `claude_conversations.json`, `claude_conversations_export.json`, `claude_conversations_YYYY-MM-DD.json`

### Data Processing Workflow
1. Place JSON files in the project root.
2. Run: `python load_conversations.py`

## Running the Application
`streamlit run Home.py` (http://localhost:8501)

### Using the Application
1. Search Conversations: Semantic search bar, relevance threshold, conversation details, similar conversations.
2. Topic Map: Visualize relationships, explore conversations, physics-based layout.

## Project Structure
(See memlog/memlog.md for project structure)

## Key Components
- `conversation_vector_store.py`: Manages vector embeddings and search.
- `load_conversations.py`: Processes and loads conversations.
- `Home.py`: Main Streamlit interface.
- `1_Topic_Map.py`: Topic visualization.

## Performance Optimizations
- Batch processing, efficient embedding generation, memory-conscious chunk processing, Qdrant search, progress tracking, error handling.

## Recent Changes
(See memlog/memlog.md for recent changes)

## System Architecture
- Data Ingestion: Raw JSON files are split into chunks.
- Vector Processing: Text extraction, embedding generation, vector storage.
- Search & Visualization: Semantic search, topic visualization, similar conversation discovery.
- Detailed diagram: `memlog/data_flow.md`

## Project Progress
(See memlog/memlog.md)

## Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request.

## License
MIT License

## Contact
Kurt Overmier (kurt@kurtovermier.com, smartbrandstrategies.com)

## Acknowledgments
- Ollama, Qdrant, Streamlit, Python Data Science Ecosystem


### Notes & Decisions
- Design decisions and rationale for key features.
- Architectural choices and their justifications.
- Key constraints and limitations.

### Resources
- Links to relevant documentation, libraries, and tools used in the project.
