# History RAG

Chat with your browsing history. A Chrome extension that syncs your browsing history into a local RAG pipeline with hybrid retrieval (dense + BM25 + Reciprocal Rank Fusion).

## Architecture

```
Chrome Extension → POST /ingest → FastAPI → Embed → ChromaDB + BM25
                   POST /chat   → FastAPI → Retrieve → Ollama LLM → Answer
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Ollama running locally (`ollama pull llama3.2:3b && ollama pull nomic-embed-text`)
- Chrome browser

### Run (Development)
```bash
docker compose --profile dev up
```

### Run (Production)
```bash
docker compose --profile prod up
```

### Run Tests
```bash
docker compose --profile test run backend-test
```

### Install Chrome Extension
1. Open `chrome://extensions`
2. Enable Developer Mode
3. Click "Load unpacked" → select `extension/` folder

## Release Versions

| Version | Features |
|---------|----------|
| v0.1.0  | History sync, hybrid retrieval, time-aware filtering |
| v0.2.0  | LLM-powered answers via Ollama (planned) |
| v0.3.0  | SQLite analytics, query classification (planned) |
| v0.4.0  | Live URL fetch at query time (planned) |

## LLMOps

- **Environments**: dev / test / prod via Docker Compose profiles
- **CI/CD**: GitHub Actions runs evals on every PR
- **Experiment tracking**: MLflow at localhost:5000
- **Prompt versioning**: `prompts/` directory (phase 2)
