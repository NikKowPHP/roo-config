# Vector Database Agent Tool Documentation

## Project Overview
The Vector Database Agent Tool provides a portable CLI for AI agents to index and query codebases using semantic search. Key features include:
- Code indexing with automatic chunking
- Natural language query interface
- Incremental file updates
- Configurable indexing settings

## Installation
```bash
# Install the package locally
pip install .

# Verify installation
vdb-index --help
vdb-tool --help
```

## Usage Examples
### Indexing a codebase
```bash
vdb-index
```

### Querying the codebase
```bash
vdb-tool query "how is authentication handled?"
```

### Updating a specific file
```bash
vdb-tool update src/utils/auth.py
```

## Configuration
Create `vdb-config.ini` in your project root:
```ini
[main]
model_name = all-MiniLM-L6-v2
qdrant_url = http://localhost:6333
collection_name = my-project

[scanning]
ignore_list = .git,.venv,node_modules
file_extensions = .py,.js,.md
```

## Architecture Overview
![System Architecture](architecture.png)

1. **Indexer**: Processes files and stores vectors in Qdrant
2. **Tool**: Provides query and update functionality
3. **Config**: Centralizes settings and model initialization
4. **Vector DB**: Qdrant database for storing and searching vectors