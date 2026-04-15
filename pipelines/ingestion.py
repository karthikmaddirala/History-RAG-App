from urllib.parse import urlparse
from services import embeddings, vectorstore, bm25_index
from config import EMBED_BATCH_SIZE


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""

def _embed_text(title: str, domain: str) -> str:
    return f"{title} — {domain}"

def ingest(entries: list[dict]) -> int:
    """
    entries: [{url, title, visit_time (unix int), visit_count}]
    Embeds in batches of EMBED_BATCH_SIZE and upserts to ChromaDB.
    """
    if not entries:
        return 0

    ids, docs, metas = [], [], []
    for e in entries:
        url = e["url"]
        title = e.get("title") or url
        domain = _domain(url)
        ids.append(url)  # url is a stable unique id
        docs.append(_embed_text(title, domain))
        metas.append({
            "url": url,
            "title": title,
            "domain": domain,
            "visit_time": int(e.get("visit_time", 0)),
            "visit_count": int(e.get("visit_count", 1)),
        })

    total = 0


    for i in range(0, len(docs), EMBED_BATCH_SIZE):
        batch_docs = docs[i:i + EMBED_BATCH_SIZE]
        batch_ids = ids[i:i + EMBED_BATCH_SIZE]
        batch_metas = metas[i:i + EMBED_BATCH_SIZE]
        vectors = embeddings.embed_texts(batch_docs)
        vectorstore.upsert(batch_ids, vectors, batch_docs, batch_metas)
        total += len(batch_docs)

    bm25_index.rebuild()  # keep sparse index in sync
    return total


# Example usage with sample data
samples = [
    {
        "url": "https://example.com",
        "title": "Example Domain",
        "visit_time": 1633024800,
        "visit_count": 5
    },
    {
        "url": "https://openai.com",
        "title": "OpenAI",
        "visit_time": 1633111200,
        "visit_count": 10
    },
    {
        "url": "https://github.com",
        "title": "GitHub",
        "visit_time": 1633197600,
        "visit_count": 3
    }
]

ingest(samples)