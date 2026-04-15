import re
import time
from services import embeddings, vectorstore, bm25_index
from config import TOP_K
import pandas as pd

_TIME_PATTERNS = [
    (re.compile(r"\btoday\b", re.I),       lambda: 1 * 86400),
    (re.compile(r"\byesterday\b", re.I),   lambda: 2 * 86400),
    (re.compile(r"\blast week\b", re.I),   lambda: 7 * 86400),
    (re.compile(r"\blast month\b", re.I),  lambda: 30 * 86400),
    (re.compile(r"\bthis year\b", re.I),   lambda: 365 * 86400),
]

def parse_time_expression(query: str):
    """Return (cleaned_query, time_filter_or_None)."""
    now = int(time.time())
    for pat, span in _TIME_PATTERNS:
        if pat.search(query):
            cleaned = pat.sub("", query).strip()
            return cleaned, {"$gte": now - span()}
    return query, None

def _rrf(dense_hits, sparse_hits, k_final, c=60):
    """Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    meta_by_id: dict[str, dict] = {}
    for rank, h in enumerate(dense_hits):
        scores[h["id"]] = scores.get(h["id"], 0) + 1 / (c + rank)
        meta_by_id[h["id"]] = h["metadata"]
    for rank, h in enumerate(sparse_hits):
        scores[h["id"]] = scores.get(h["id"], 0) + 1 / (c + rank)
        meta_by_id[h["id"]] = h["metadata"]
    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k_final]
    return [{"id": i, "score": s, "metadata": meta_by_id[i]} for i, s in fused]

def retrieve(query: str, k: int = TOP_K):
    cleaned, time_filter = parse_time_expression(query)

    # Dense
    qvec = embeddings.embed_texts([cleaned])[0]
    raw = vectorstore.query(qvec, k=k * 2, where={"visit_time": time_filter} if time_filter else None)
    df = pd.DataFrame({
        "query": query,
        "id": raw["ids"][0],
        "document": raw["documents"][0],
        "distance": raw["distances"][0]
    })
    print(df.to_markdown(index=False))

    dense_hits = [
        {"id": raw["ids"][0][i], "metadata": raw["metadatas"][0][i]}
        for i in range(len(raw["ids"][0]))
    ]

    # Sparse
    sparse_hits = bm25_index.query(cleaned, k=k * 2, time_filter=time_filter)

    return _rrf(dense_hits, sparse_hits, k_final=k)