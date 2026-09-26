"""Composition root: the only place that chooses concrete adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO

from opspilot.adapters.embeddings import HashingEmbedder, SentenceTransformerEmbedder
from opspilot.adapters.memory_index import InMemoryIndex
from opspilot.adapters.offline_llm import OfflineLLM
from opspilot.adapters.telemetry import FixtureTelemetry
from opspilot.agent.graph import AgentConfig, IncidentAgent
from opspilot.agent.toolkit import build_default_tools
from opspilot.agent.tools import ToolRegistry
from opspilot.config import Settings
from opspilot.observability.metrics import MetricsLogger
from opspilot.ports import Embedder, LLMClient, SearchIndex, TelemetrySource
from opspilot.resilience.circuit_breaker import CircuitBreaker
from opspilot.resilience.resilient_llm import ResilientLLM
from opspilot.resilience.semantic_cache import SemanticCache
from opspilot.retrieval.hybrid import HybridRetriever
from opspilot.services.diagnosis import DiagnosisService
from opspilot.services.ingestion import IngestionService


@dataclass
class Container:
    settings: Settings
    embedder: Embedder
    index: SearchIndex
    retriever: HybridRetriever
    telemetry: TelemetrySource
    tools: ToolRegistry
    llm: LLMClient
    agent: IncidentAgent
    diagnosis: DiagnosisService
    ingestion: IngestionService


def _embedder(settings: Settings) -> Embedder:
    if settings.embedder == "sentence-transformers":
        return SentenceTransformerEmbedder()
    return HashingEmbedder()


def _index(settings: Settings, dimension: int) -> SearchIndex:
    if settings.index == "postgres":
        from opspilot.adapters.pgvector_index import PgVectorIndex

        return PgVectorIndex(settings.database_url, dimension)
    return InMemoryIndex(dimension)


def _llm(settings: Settings) -> LLMClient:
    if settings.llm_provider == "offline":
        return OfflineLLM()
    from opspilot.adapters.claude import ClaudeLLM

    inner = ClaudeLLM(
        settings.model, provider=settings.llm_provider, aws_region=settings.aws_region
    )
    return ResilientLLM(inner, CircuitBreaker("claude", failure_threshold=5, reset_timeout=30))


def build_container(
    settings: Settings,
    *,
    llm: LLMClient | None = None,
    telemetry: TelemetrySource | None = None,
    metrics_stream: TextIO | None = None,
) -> Container:
    """Wire the application. Tests and the CLI inject fakes via the keyword arguments."""
    embedder = _embedder(settings)
    index = _index(settings, embedder.dimension)
    retriever = HybridRetriever(index, embedder)
    telemetry = telemetry or FixtureTelemetry(settings.telemetry_dir)
    tools = build_default_tools(telemetry, retriever)
    llm = llm or _llm(settings)
    agent = IncidentAgent(
        llm,
        retriever,
        tools,
        AgentConfig(
            retrieval_k=settings.retrieval_k,
            max_steps=settings.max_agent_steps,
            max_tool_calls=settings.max_tool_calls,
            token_budget=settings.token_budget,
        ),
    )
    cache = SemanticCache(
        embedder, threshold=settings.cache_similarity, ttl_seconds=settings.cache_ttl_seconds
    )
    return Container(
        settings=settings,
        embedder=embedder,
        index=index,
        retriever=retriever,
        telemetry=telemetry,
        tools=tools,
        llm=llm,
        agent=agent,
        diagnosis=DiagnosisService(
            agent,
            cache,
            metrics_factory=lambda operation: MetricsLogger(
                operation, stream=metrics_stream, dimensions={"Stage": settings.stage.value}
            ),
        ),
        ingestion=IngestionService(index, embedder),
    )
