import os
import qdrant_client
from qdrant_client.http.models import Distance, PointStruct, UpdateStatus, VectorParams
from sentence_transformers import SentenceTransformer
import uuid

# --- CONFIGURATION ---
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "project_codebase"
MODEL_NAME = 'all-MiniLM-L6-v2'  # Small, fast, effective model for code embeddings

# --- Initialize clients ---
model = SentenceTransformer(MODEL_NAME)
client = qdrant_client.QdrantClient(url=QDRANT_URL)

def chunk_code(file_content, file_path, chunk_size=512, overlap=100):
    """Breaks code into overlapping chunks."""
    chunks = []
    lines = file_content.splitlines()
    line_count = len(lines)
    current_line = 0
    
    while current_line < line_count:
        end_line = min(current_line + 20, line_count)  # Chunk by 20 lines at a time
        chunk_text = "\n".join(lines[current_line:end_line])
        
        chunks.append({
            "text": chunk_text,
            "file_path": file_path,
            "start_line": current_line + 1,
            "end_line": end_line
        })
        current_line += 15  # Overlap of 5 lines
    
    return chunks

def index_repository(root_dir):
    """Walks through repository, chunks files, and upserts them to Qdrant."""
    
    # Ensure collection exists
    try:
        client.get_collection(collection_name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' already exists.")
    except Exception as e:
        print(f"Collection '{COLLECTION_NAME}' not found. Creating it now.")
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=Distance.COSINE
            ),
        )

    # File discovery configuration
    ignore_list = ['.git', 'node_modules', '.vscode', 'dist', 'build', '.DS_Store', 'repomix-output.xml']
    file_extensions = ['.js', '.ts', '.tsx', '.py', '.md', '.sh', '.yaml']
    points_to_upsert = []
    
    for root, dirs, files in os.walk(root_dir):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_list]

        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    chunks = chunk_code(content, file_path)
                    
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
                        points_to_upsert.append(point)
                
                except Exception as e:
                    print(f"  - Error processing {file_path}: {e}")

    # Batch upsert points
    if points_to_upsert:
        print(f"\nUpserting {len(points_to_upsert)} points to Qdrant...")
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points_to_upsert,
            wait=True
        )
        print("Upsert complete.")

if __name__ == "__main__":
    index_repository('.')