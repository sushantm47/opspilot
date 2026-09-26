# OpsPilot

An agentic RAG copilot for on-call incident response (work in progress).

This first milestone contains the foundation:

- **Hybrid retrieval**: markdown-aware chunking with contextual headers, BM25, dense
  vectors, and Reciprocal Rank Fusion
- **Vector store adapters**: in-memory (NumPy) and PostgreSQL + pgvector (HNSW + full-text)
- **Resilience**: exponential backoff with full jitter, circuit breaker, semantic cache
- **Observability**: JSON logs with request IDs, CloudWatch Embedded Metric Format
- **Stage-aware config**: local → beta → gamma → prod
- Hexagonal architecture: the core depends only on interfaces in `ports/`

Next milestone: the incident agent (tool loop + guardrails + grounding verifier),
FastAPI service, MCP server, evals, and AWS CDK infrastructure.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
