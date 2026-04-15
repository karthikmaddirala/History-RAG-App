from fastapi import APIRouter
from pydantic import BaseModel
from pipelines import ingestion, retrieval

router = APIRouter()

class HistoryEntry(BaseModel):
    url: str
    title: str | None = None
    visit_time: int = 0
    visit_count: int = 1

class IngestRequest(BaseModel):
    entries: list[HistoryEntry]

class ChatRequest(BaseModel):
    query: str

@router.post("/ingest")
def ingest_route(req: IngestRequest):
    n = ingestion.ingest([e.model_dump() for e in req.entries])
    return {"ingested": n}

@router.post("/chat")
def chat_route(req: ChatRequest):
    hits = retrieval.retrieve(req.query)
    # TODO: pass hits to LLM as context and return generated answer
    return {"hits": hits}
