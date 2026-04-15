from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

_model: SentenceTransformer | None = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of strings. Used by both ingestion and retrieval."""
    if not texts:
        return []
    vectors = _get_model().encode(texts, batch_size=64, show_progress_bar=False)
    return vectors.tolist()
