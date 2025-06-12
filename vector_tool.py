import argparse
import json
import qdrant_client
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# --- CONFIGURATION (matches indexer.py) ---
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "project_codebase"
MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Initialize clients ---
model = SentenceTransformer(MODEL_NAME)
client = qdrant_client.QdrantClient(url=QDRANT_URL)

def chunk_code(file_content, file_path):
    """Reusable chunking logic from indexer.py"""
    chunks = []
    lines = file_content.splitlines()
    line_count = len(lines)
    current_line = 0
    
    while current_line < line_count:
        end_line = min(current_line + 20, line_count)
        chunk_text = "\n".join(lines[current_line:end_line])
        chunks.append({
            "text": chunk_text,
            "file_path": file_path,
            "start_line": current_line + 1,
            "end_line": end_line
        })
        current_line += 15  # 5-line overlap
    
    return chunks

def update_file(file_path):
    """Updates vectors for a single file"""
    print(f"Updating vectors for: {file_path}")
    
    # Delete existing vectors for this file
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[FieldCondition(key="file_path", match=MatchValue(value=file_path))]
        )
    )
    print("  - Deleted old entries")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_code(content, file_path)
        points = []
        
        for chunk in chunks:
            vector = model.encode(chunk["text"]).tolist()
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "file_path": chunk["file_path"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "code_chunk": chunk["text"]
                }
            )
            points.append(point)
        
        if points:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True
            )
            print(f"  - Upserted {len(points)} new chunks")
    
    except FileNotFoundError:
        print(f"  - File not found: {file_path}. Assuming deletion, no new vectors added.")
    except Exception as e:
        print(f"  - Error updating {file_path}: {e}")

def query_code(query_text, limit=5):
    """Searches codebase with natural language query"""
    query_vector = model.encode(query_text).tolist()
    
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        with_payload=True
    )
    
    # Format results for JSON output
    formatted = []
    for hit in results:
        formatted.append({
            "score": hit.score,
            "file_path": hit.payload["file_path"],
            "start_line": hit.payload["start_line"],
            "code_chunk": hit.payload["code_chunk"]
        })
    
    print(json.dumps(formatted, indent=2))

# --- Command-line interface ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vector DB tool for codebase context")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Update command
    update_parser = subparsers.add_parser('update', help='Update vectors for a file')
    update_parser.add_argument('file_path', help='Path to file to update')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the codebase')
    query_parser.add_argument('query_text', help='Natural language query')
    query_parser.add_argument('--limit', type=int, default=5, help='Number of results')

    args = parser.parse_args()
    
    if args.command == 'update':
        update_file(args.file_path)
    elif args.command == 'query':
        query_code(args.query_text, args.limit)