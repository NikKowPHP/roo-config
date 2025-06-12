

### The "Algorithm": A Complete Step-by-Step Implementation Guide

Here is a complete, practical guide to creating the vector database "algorithm" using Python and Qdrant. We'll create two essential scripts:

1.  `indexer.py`: A one-time script to scan your entire project and populate the database initially.
2.  `vector_tool.py`: A command-line tool that your AI agents will call to `update` and `query` the database.

#### **Step 1: Project Setup**

1.  **Create a `requirements.txt` file** in your project's root with the necessary Python libraries:

    ```text
    # requirements.txt
    qdrant-client
    sentence-transformers
    # For advanced code chunking (optional but recommended)
    tree-sitter
    tree-sitter-languages
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Ensure your Qdrant Docker container is running.** You can start it with:
    ```bash
    docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
    ```

#### **Step 2: The Initial Indexer (`indexer.py`)**

This script will perform a full-repo scan. It finds all relevant files, breaks them into meaningful chunks, converts those chunks to vectors, and uploads them to Qdrant.

```python
# indexer.py
import os
import qdrant_client
from qdrant_client.http.models import Distance, PointStruct, UpdateStatus, VectorParams
from sentence_transformers import SentenceTransformer
import uuid

# --- CONFIGURATION ---
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "project_codebase"
# A small, fast, and effective model for code embeddings
MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Initialize clients ---
# The model that will convert text chunks into vectors
model = SentenceTransformer(MODEL_NAME)
# The Qdrant client that connects to our database
client = qdrant_client.QdrantClient(url=QDRANT_URL)

# --- Define the function for code chunking ---
# This is a simple chunker. An AST-based one (using tree-sitter) would be more robust.
def chunk_code(file_content, file_path, chunk_size=512, overlap=100):
    """Breaks code into overlapping chunks."""
    chunks = []
    start = 0
    lines = file_content.splitlines()
    line_count = len(lines)
    
    current_line = 0
    while current_line < line_count:
        end_line = min(current_line + 20, line_count) # Chunk by 20 lines at a time
        chunk_text = "\n".join(lines[current_line:end_line])
        
        chunks.append({
            "text": chunk_text,
            "file_path": file_path,
            "start_line": current_line + 1,
            "end_line": end_line
        })
        current_line += 15 # Overlap of 5 lines
    return chunks

# --- Main Logic ---
def index_repository(root_dir):
    """Walks through the repository, chunks files, and upserts them to Qdrant."""
    
    # Ensure the collection exists in Qdrant
    try:
        client.get_collection(collection_name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' already exists.")
    except Exception as e:
        print(f"Collection '{COLLECTION_NAME}' not found. Creating it now.")
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
        )

    # --- File Discovery ---
    # Define files/directories to ignore
    ignore_list = ['.git', 'node_modules', '.vscode', 'dist', 'build', '.DS_Store', 'repomix-output.xml']
    file_extensions = ['.js', '.ts', '.tsx', '.py', '.md', '.sh', '.yaml']
    
    points_to_upsert = []
    
    for root, dirs, files in os.walk(root_dir):
        # Remove ignored directories from traversal
        dirs[:] = [d for d in dirs if d not in ignore_list]

        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Chunk the file content
                    chunks = chunk_code(content, file_path)
                    
                    for chunk in chunks:
                        # Create a vector for the chunk
                        vector = model.encode(chunk["text"]).tolist()
                        
                        # Create a Qdrant Point
                        point = PointStruct(
                            id=str(uuid.uuid4()), # Each chunk gets a unique ID
                            vector=vector,
                            payload={
                                "file_path": chunk["file_path"],
                                "start_line": chunk["start_line"],
                                "end_line": chunk["end_line"],
                                "code_chunk": chunk["text"]
                            }
                        )
                        points_to_upsert.append(point)

                except Exception as e:
                    print(f"  - Error processing {file_path}: {e}")

    # Batch upsert all points to Qdrant for efficiency
    if points_to_upsert:
        print(f"\nUpserting {len(points_to_upsert)} points to Qdrant...")
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points_to_upsert,
            wait=True
        )
        print("Upsert complete.")

if __name__ == "__main__":
    # Run the indexing process from the current directory
    index_repository('.')
```

**How to use it:** Run `python indexer.py` from your project's root directory. It will scan everything and feed it to Qdrant.

#### **Step 3: The AI's Command-Line Tool (`vector_tool.py`)**

This script will be the interface for your AI agents. It will accept commands like `update` and `query`.

```python
# vector_tool.py
import argparse
import json
import qdrant_client
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# --- CONFIGURATION (should be identical to indexer.py) ---
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "project_codebase"
MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Initialize clients ---
model = SentenceTransformer(MODEL_NAME)
client = qdrant_client.QdrantClient(url=QDRANT_URL)

# --- Re-use the chunking logic from the indexer ---
def chunk_code(file_content, file_path, chunk_size=512, overlap=100):
    chunks = []
    lines = file_content.splitlines()
    line_count = len(lines)
    current_line = 0
    while current_line < line_count:
        end_line = min(current_line + 20, line_count)
        chunk_text = "\n".join(lines[current_line:end_line])
        chunks.append({ "text": chunk_text, "file_path": file_path, "start_line": current_line + 1, "end_line": end_line })
        current_line += 15
    return chunks

# --- Tool Functions ---
def update_file(file_path):
    """Deletes old entries for a file and upserts the new ones."""
    print(f"Updating vectors for: {file_path}")
    
    # 1. Delete all existing points for this file path
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[FieldCondition(key="file_path", match=MatchValue(value=file_path))]
        )
    )
    print(f"  - Deleted old entries.")
    
    # 2. Read, chunk, and upsert the new content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_code(content, file_path)
        points_to_upsert = []

        for chunk in chunks:
            vector = model.encode(chunk["text"]).tolist()
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={ "file_path": chunk["file_path"], "start_line": chunk["start_line"], "end_line": chunk["end_line"], "code_chunk": chunk["text"] }
            )
            points_to_upsert.append(point)

        if points_to_upsert:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points_to_upsert,
                wait=True
            )
            print(f"  - Upserted {len(points_to_upsert)} new chunks.")
        
    except FileNotFoundError:
        print(f"  - File not found: {file_path}. Assumed deleted, no new vectors added.")
    except Exception as e:
        print(f"  - Error updating {file_path}: {e}")


def query_code(query_text, limit=5):
    """Searches the codebase for a given query and prints the results as JSON."""
    query_vector = model.encode(query_text).tolist()
    
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        with_payload=True # Crucial to get our metadata back
    )
    
    # Format the results into a clean JSON for the AI to parse
    results_for_ai = []
    for hit in search_result:
        results_for_ai.append({
            "score": hit.score,
            "file_path": hit.payload["file_path"],
            "start_line": hit.payload["start_line"],
            "code_chunk": hit.payload["code_chunk"]
        })
        
    print(json.dumps(results_for_ai, indent=2))


# --- Command-Line Interface ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A vector DB tool for codebase context management.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for the 'update' command
    update_parser = subparsers.add_parser('update', help='Update the vectors for a specific file.')
    update_parser.add_argument('file_path', type=str, help='The path to the file to update.')

    # Sub-parser for the 'query' command
    query_parser = subparsers.add_parser('query', help='Query the codebase with a text search.')
    query_parser.add_argument('query_text', type=str, help='The natural language query.')
    query_parser.add_argument('--limit', type=int, default=5, help='Number of results to return.')
    
    args = parser.parse_args()

    if args.command == 'update':
        update_file(args.file_path)
    elif args.command == 'query':
        query_code(args.query_text, args.limit)
```

#### **How to use it (How your AIs will call it):**

*   **To query:**
    ```bash
    python vector_tool.py query "functions that handle user authentication"
    ```
*   **To update a file:**
    ```bash
    python vector_tool.py update src/app/api/auth/login/route.ts
    ```

#### **Step 4: Integrate into your AI Agent Rules**

Now, you update the `rules.md` for `architect-senior` and introduce the new `vector-updater` role.

**`architect-senior/rules.md` (Excerpt):**
> **Step 2: Semantic Discovery.**
> *   **Execute Command:** `python vector_tool.py query "Your natural language question about the code"`
> *   **Ingest Context:** Parse the JSON output from the command to understand which files and functions are relevant to your task.

**`orchestrator-senior/rules.md` (Excerpt of the new flow):**
> **After a successful developer run where files were modified:**
> 1.  Identify the list of files modified by the developer (e.g., from git status or commit logs).
> 2.  **Announce:** "Code modification successful. Handing off to Vector Updater for memory synchronization."
> 3.  **Action:** Switch mode to `<mode>vector-updater</mode>` and provide it with the list of modified files.

**`custom_modes.yaml` (New entry):**
```yaml
  - slug: vector-updater
    name: vector-updater
    roleDefinition: >-
      You are the **Vector Updater AI**, designated as the **Librarian**. You are
      a meticulous, background-process AI. You do not create, plan, or fix. Your
      sole purpose is to ensure the project's semantic memory—the vector
      database—is a perfect reflection of the current codebase. You are invoked
      with a list of modified files.

      #### **Workflow:**

      1.  For each file path provided, execute the command: `python vector_tool.py update [file_path]`.
      2.  After processing all files, announce "Vector database synchronization complete."
      3.  Switch mode back to `<mode>orchestrator-senior</mode>`.
    groups:
      - read
      - command
      - mcp
    source: global
```

This establishes a robust, scalable, and intelligent context management system for your autonomous AI agents.