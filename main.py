from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.api import router
from services import bm25_index

@asynccontextmanager
async def lifespan(app: FastAPI):
    bm25_index.rebuild()  # rebuild sparse index from ChromaDB on startup
    yield

app = FastAPI(title="Browsing History RAG", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to chrome-extension://<id> in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
