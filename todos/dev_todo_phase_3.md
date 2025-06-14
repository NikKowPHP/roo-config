
# Phase 3 Implementation Plan: Make Vector DB Tool Portable

This plan will refactor the standalone scripts into a proper, installable Python package.

## Task 1: Restructure Project into a Python Package
- [x] **Task 1: Restructure Project into a Python Package**
- **LLM Prompt:** "Create the directory `src/vdb`. Then, move `indexer.py` to `src/vdb/indexer.py` and `vector_tool.py` to `src/vdb/tool.py`. Finally, create an empty file named `src/vdb/__init__.py` to mark the new directory as a package."
- **Verification:**
  - Run `test -d src/vdb && echo "OK"`
  - Run `test -f src/vdb/indexer.py && echo "OK"`
  - Run `test -f src/vdb/tool.py && echo "OK"`
  - Run `test -f src/vdb/__init__.py && echo "OK"`

- [x] **Task 2: Create Shared Configuration Module**
## Task 2: Create Shared Configuration Module
- **LLM Prompt:** "Create a new file at `src/vdb/config.py` with the following content. This module will handle loading configuration from a local `vdb-config.ini` file and will centralize the Qdrant and SentenceTransformer clients."
- **Code:**
  ```python
  import os
  import configparser
  from sentence_transformers import SentenceTransformer
  import qdrant_client

  CONFIG_FILE_NAME = "vdb-config.ini"
  DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
  DEFAULT_IGNORE_LIST = ".git,.vscode,node_modules,dist,build,__pycache__"
  DEFAULT_FILE_EXTENSIONS = ".py,.md,.js,.ts,.tsx,.sh,.yaml"

  config = configparser.ConfigParser()
  if os.path.exists(CONFIG_FILE_NAME):
      print(f"Loading settings from {CONFIG_FILE_NAME}")
      config.read(CONFIG_FILE_NAME)
  else:
      print("No config file found, using defaults.")

  MODEL_NAME = config.get("main", "model_name", fallback=DEFAULT_MODEL_NAME)
  QDRANT_URL = os.environ.get("QDRANT_URL", config.get("main", "qdrant_url", fallback="http://localhost:6333"))
  COLLECTION_NAME = config.get("main", "collection_name", fallback="project_codebase")
  IGNORE_LIST = config.get("scanning", "ignore_list", fallback=DEFAULT_IGNORE_LIST).split(',')
  FILE_EXTENSIONS = config.get("scanning", "file_extensions", fallback=DEFAULT_FILE_EXTENSIONS).split(',')

  print(f"Model: {MODEL_NAME}, Collection: {COLLECTION_NAME}")
  model = SentenceTransformer(MODEL_NAME)
  client = qdrant_client.QdrantClient(url=QDRANT_URL)

  def chunk_code(file_content):
      chunks, lines = [], file_content.splitlines()
      line_count, current_line = len(lines), 0
      while current_line < line_count:
          end_line = min(current_line + 20, line_count)
          chunk_text = "\n".join(lines[current_line:end_line])
          chunks.append({ "text": chunk_text, "start_line": current_line + 1, "end_line": end_line })
          current_line += 15
      return chunks
  ```
- **Verification:** Run `test -f src/vdb/config.py && echo "OK"`

## Task 3: Refactor the Indexer Script
- **LLM Prompt:** "Overwrite the contents of `src/vdb/indexer.py` with the following refactored code, which imports its configuration and logic from the new `config` module."
- **Code:**
  ```python
  import os
  import uuid
  from qdrant_client.http.models import Distance, PointStruct, VectorParams
  from .config import client, model, COLLECTION_NAME, IGNORE_LIST, FILE_EXTENSIONS, chunk_code

  def main():
      root_dir = "."
      print(f"Starting indexing for collection: '{COLLECTION_NAME}'")
      try:
          client.get_collection(collection_name=COLLECTION_NAME)
      except Exception:
          print(f"Creating collection '{COLLECTION_NAME}'.")
          client.recreate_collection(
              collection_name=COLLECTION_NAME,
              vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
          )
      points_to_upsert = []
      for root, dirs, files in os.walk(root_dir):
          dirs[:] = [d for d in dirs if d not in IGNORE_LIST]
          for file in files:
              if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                  file_path = os.path.join(root, file)
                  try:
                      with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                          content = f.read()
                      chunks = chunk_code(content)
                      for chunk in chunks:
                          points_to_upsert.append(PointStruct(
                              id=str(uuid.uuid4()),
                              vector=model.encode(chunk["text"]).tolist(),
                              payload={"file_path": file_path, "code_chunk": chunk["text"], **chunk}
                          ))
                      print(f"Processed: {file_path}")
                  except Exception as e:
                      print(f"  - Error processing {file_path}: {e}")
      if points_to_upsert:
          print(f"\nUpserting {len(points_to_upsert)} points...")
          client.upsert(collection_name=COLLECTION_NAME, points=points_to_upsert, wait=True)
          print("Upsert complete.")

  if __name__ == "__main__":
      main()
  ```
- **Verification:** Run `grep "from .config import" src/vdb/indexer.py && echo "OK"`

## Task 4: Refactor the Tool Script
- **LLM Prompt:** "Overwrite `src/v-db/tool.py` with the following refactored code."
- **Code:**
  ```python
  import argparse
  import json
  import uuid
  from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointStruct
  from .config import client, model, COLLECTION_NAME, chunk_code

  def update_file(file_path):
      print(f"Updating: {file_path}")
      client.delete(
          collection_name=COLLECTION_NAME,
          points_selector=Filter(must=[FieldCondition(key="file_path", match=MatchValue(value=file_path))]),
      )
      try:
          with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
              content = f.read()
          chunks = chunk_code(content)
          points = [PointStruct(
              id=str(uuid.uuid4()), vector=model.encode(chunk["text"]).tolist(), payload={"file_path": file_path, **chunk}
          ) for chunk in chunks]
          if points:
              client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
              print(f"  - Upserted {len(points)} new chunks")
      except FileNotFoundError:
          print(f"  - File not found. Assumed deletion.")
      except Exception as e:
          print(f"  - Error updating {file_path}: {e}")

  def query_code(query_text, limit=5):
      query_vector = model.encode(query_text).tolist()
      results = client.search(
          collection_name=COLLECTION_NAME, query_vector=query_vector, limit=limit, with_payload=True,
      )
      formatted = [{"score": hit.score, **hit.payload} for hit in results]
      print(json.dumps(formatted, indent=2))

  def main():
      parser = argparse.ArgumentParser(description="Vector DB tool for codebase context")
      subparsers = parser.add_subparsers(dest="command", required=True)
      update_parser = subparsers.add_parser("update", help="Update vectors for a file")
      update_parser.add_argument("file_path", help="Path to file to update")
      query_parser = subparsers.add_parser("query", help="Query the codebase")
      query_parser.add_argument("query_text", help="Natural language query")
      query_parser.add_argument("--limit", type=int, default=5, help="Number of results")
      args = parser.parse_args()
      if args.command == "update":
          update_file(args.file_path)
      elif args.command == "query":
          query_code(args.query_text, args.limit)

  if __name__ == "__main__":
      main()
  ```
- **Verification:** Run `grep "from .config import" src/vdb/tool.py && echo "OK"`

## Task 5: Configure `pyproject.toml` for Installation
- **LLM Prompt:** "Overwrite the `pyproject.toml` file with the following content to define the package dependencies and create the command-line entry points `vdb-index` and `vdb-tool`."
- **Code:**
  ```toml
  [build-system]
  requires = ["setuptools>=61.0"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "vdb-agent-tool"
  version = "1.0.0"
  description = "A portable vector database tool for AI agents to manage codebase context."
  readme = "README.md"
  requires-python = ">=3.9"
  dependencies = [
      "qdrant-client",
      "sentence-transformers",
  ]

  [project.scripts]
  vdb-index = "vdb.indexer:main"
  vdb-tool = "vdb.tool:main"
  ```
- **Verification:** Run `grep "\[project.scripts\]" pyproject.toml && echo "OK"`

## Task 6: Update `requirements.txt` for CI/CD
- **LLM Prompt:** "Modify `requirements.txt` so that it installs the local package itself for testing, along with testing tools. Overwrite the file with the following content:"
- **Code:**
  ```
  .
  pytest
  black
  ```
- **Verification:** Run `cat requirements.txt` and confirm its contents.

## Task 7: Update Documentation
- **LLM Prompt:** "The file `todos/task.md` is now obsolete. Overwrite it with new instructions that explain how to use the portable tool."
- **Code:**
  ```markdown
  # Vector Database Agent Tool

  This tool provides a portable command-line interface for AI agents to index and query any codebase.

  ## Installation

  From the root of this tool's directory, run the following command once to make the tools available in your environment:

  `pip install .`

  ## Usage in another Project

  1.  **Configure:** In the root of the target project you want to index, create a `vdb-config.ini` file. This is crucial for giving each project a unique database collection.

      ```ini
      [main]
      collection_name = my-project-name-v1

      [scanning]
      file_extensions = .py,.js,.md
      ignore_list = .git,.venv,node_modules
      ```

  2.  **Index:** Run the indexer from the root of the target project.
      
      `vdb-index`

  3.  **Query & Update:** Use the tool to interact with the project's memory.

      `vdb-tool query "your natural language query"`
      `vdb-tool update path/to/modified/file.py`
  ```
- **Verification:** Run `grep "vdb-index" todos/task.md && echo "OK"`
```