import os

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_data")
COLLECTION_NAME = "browsing_history"
EMBED_BATCH_SIZE = 1000
TOP_K = 10
EXTENSION_ORIGIN = os.getenv("EXTENSION_ORIGIN", "chrome-extension://*")