import chromadb
from config import CHROMA_PATH, COLLECTION_NAME

_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = _client.get_or_create_collection(name=COLLECTION_NAME)

def upsert(ids, embeddings, documents, metadatas):
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

def query(query_embedding, k, where=None):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where,
        include=["documents", "distances", "metadatas"],
    )

def all_documents():
    """Used by bm25_index to rebuild on startup."""
    return collection.get(include=["documents", "metadatas"])
