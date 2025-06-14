# Technical Design Specification: Vector Database Agent Tool

## 1. System Overview
The Vector Database Agent Tool is a Python-based CLI application that provides semantic search capabilities for codebases. It indexes code into a vector database and allows natural language queries to retrieve relevant code segments.

## 2. Architecture Diagram
```
[User Terminal] 
     │
     ▼
[CLI Interface] 
     │
     ├──▶ [Indexing Module] ───▶ [Qdrant Vector DB]
     │
     └──▶ [Query Module] ◀───┘
```

## 3. Component Specifications
### 3.1 CLI Interface
- **Input:** Commands (`index`, `query`, `update`)
- **Output:** Human-readable results
- **Dependencies:** `argparse` for command parsing

### 3.2 Indexing Module
- **Input:** Directory paths, file patterns
- **Processing:**
  - File parsing and chunking
  - Embedding generation with Sentence Transformers
  - Metadata extraction (file path, line numbers)
- **Output:** Vector embeddings stored in Qdrant

### 3.3 Query Module
- **Input:** Natural language query string
- **Processing:**
  - Query embedding generation
  - Vector similarity search
  - Result ranking
- **Output:** Top matching code segments with context

### 3.4 Configuration Manager
- **Storage:** INI-formatted config file
- **Parameters:**
  - Database connection settings
  - Embedding model selection
  - Chunk size and overlap
  - Watched directories

## 4. Data Flow
### 4.1 Indexing Process
1. User runs `vdb index /path/to/code`
2. System scans directory for source files
3. Files are split into logical chunks
4. Chunks are converted to embeddings
5. Embeddings stored in Qdrant with metadata

### 4.2 Query Process
1. User runs `vdb query "how to parse JSON"`
2. Query is embedded using same model
3. Similarity search in vector DB
4. Top results formatted and displayed

## 5. Database Schema
### 5.1 Qdrant Collections
- **Collection Name:** code_embeddings
- **Fields:**
  - `id`: UUID (primary key)
  - `embedding`: vector (768 dimensions)
  - `metadata`: JSON blob
    - file_path: string
    - start_line: int
    - end_line: int
    - language: string
    - content_hash: string

## 6. API Specifications
### 6.1 Internal Python API
```python
class VectorDB:
    def index_directory(path: str, config: Config) -> int
    def query_code(query: str, top_k: int=5) -> List[CodeResult]

class CodeResult:
    file_path: str
    start_line: int
    end_line: int
    content: str
    score: float
```

## 7. Error Handling
- File system errors during indexing
- Database connection failures
- Invalid query syntax
- Configuration validation errors