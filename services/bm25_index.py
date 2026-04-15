import re
from rank_bm25 import BM25Okapi
from services import vectorstore

_bm25: BM25Okapi | None = None
_ids: list[str] = []
_metadatas: list[dict] = []

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())

def rebuild():
    """Rebuild the in-memory BM25 index from ChromaDB. Call on startup and after big ingests."""
    global _bm25, _ids, _metadatas
    data = vectorstore.all_documents()
    _docs = data.get("documents") or []
    _ids = data.get("ids") or []
    _metadatas = data.get("metadatas") or []
    if not _docs:
        _bm25 = None
        return
    _bm25 = BM25Okapi([_tokenize(d) for d in _docs])

def query(text: str, k: int, time_filter: dict | None = None):
    if _bm25 is None:
        return []
    scores = _bm25.get_scores(_tokenize(text))
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    hits = []
    for idx, score in ranked:
        meta = _metadatas[idx]
        if time_filter:
            ts = meta.get("visit_time", 0)
            if "$gte" in time_filter and ts < time_filter["$gte"]:
                continue
            if "$lte" in time_filter and ts > time_filter["$lte"]:
                continue
        hits.append({"id": _ids[idx], "score": float(score), "metadata": meta})
        if len(hits) >= k:
            break
    return hits
