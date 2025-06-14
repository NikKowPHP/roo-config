import argparse
import json
import uuid
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointStruct
from vdb.config import client, model, COLLECTION_NAME, chunk_code

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
