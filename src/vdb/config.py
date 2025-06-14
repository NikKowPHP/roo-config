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