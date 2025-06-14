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
