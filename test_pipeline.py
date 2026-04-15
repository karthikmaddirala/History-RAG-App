"""
Sanity-check the ingestion + retrieval pipeline without the Chrome extension.
Run from the backend/ directory:  python test_pipeline.py
"""
import time
from pipelines import ingestion, retrieval
from services import bm25_index

now = int(time.time())
DAY = 86400

FAKE_HISTORY = [
    {"url": "https://stackoverflow.com/q/1/cors-fastapi",
     "title": "How to fix CORS errors in FastAPI",
     "visit_time": now - 2 * DAY, "visit_count": 3},
    {"url": "https://fastapi.tiangolo.com/tutorial/cors/",
     "title": "CORS Middleware - FastAPI docs",
     "visit_time": now - 2 * DAY, "visit_count": 1},
    {"url": "https://github.com/encode/starlette/issues/123",
     "title": "Starlette CORS preflight bug",
     "visit_time": now - 40 * DAY, "visit_count": 1},
    {"url": "https://arxiv.org/abs/1706.03762",
     "title": "Attention Is All You Need",
     "visit_time": now - 10 * DAY, "visit_count": 5},
    {"url": "https://news.ycombinator.com/item?id=999",
     "title": "Show HN: A Rust-based vector database",
     "visit_time": now - 3 * DAY, "visit_count": 1},
    {"url": "https://www.youtube.com/watch?v=abc",
     "title": "Transformers explained visually",
     "visit_time": now - 8 * DAY, "visit_count": 2},
    {"url": "https://docs.trychroma.com/usage-guide",
     "title": "ChromaDB Usage Guide",
     "visit_time": now - 1 * DAY, "visit_count": 4},
    {"url": "https://realpython.com/python-async/",
     "title": "Async IO in Python: A Complete Walkthrough",
     "visit_time": now - 15 * DAY, "visit_count": 1},
    {"url": "https://en.wikipedia.org/wiki/BM25",
     "title": "Okapi BM25 - Wikipedia",
     "visit_time": now - 5 * DAY, "visit_count": 2},
    {"url": "https://substack.com/p/rlhf-explained",
     "title": "RLHF, explained simply",
     "visit_time": now - 6 * DAY, "visit_count": 1},
]

print(f"Ingesting {len(FAKE_HISTORY)} fake entries...")
n = ingestion.ingest(FAKE_HISTORY)
print(f"  -> ingested {n}\n")

# bm25_index.rebuild() is already called inside ingest(), but call again to be explicit
#bm25_index.rebuild()

QUERIES = [
    "that CORS bug I fixed",                # tests dense + BM25 keyword overlap
    "transformers paper",                   # semantic match (arxiv title doesn't say "transformers")
    "vector database",                      # should hit chroma docs + HN post
    "the CORS bug last week",               # tests time filter (excludes the 40-day-old one)
    "BM25",                                 # exact-token query, BM25 should win
]

for q in QUERIES:
   # print(f"Q: {q}")
    hits = retrieval.retrieve(q, k=3)
    if not hits:
        print("  (no hits)")
    for h in hits:
        m = h["metadata"]
        age_days = (now - m["visit_time"]) // DAY
       # print(f"  [{age_days:>3}d ago] {m['title']}  ({m['domain']})")
   # print()
