"""FastAPI application factory.

Run locally:  uvicorn opspilot.api.app:create_app --factory --reload
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from opspilot import __version__
from opspilot.api.schemas import AlertRequest, DiagnosisResponse, HealthResponse, IngestResponse
from opspilot.config import Settings, Stage
from opspilot.container import Container, build_container
from opspilot.domain.errors import DependencyUnavailableError, InvalidRequestError
from opspilot.observability.logging import configure_logging, request_id_var

log = logging.getLogger(__name__)


def _default_container() -> Container:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    return build_container(settings)


def create_app(container: Container | None = None) -> FastAPI:
    # Bind a non-Optional name so the closures below are well-typed.
    c: Container = container if container is not None else _default_container()
    # Pre-prod convenience; prod ingests through the deployment pipeline instead.
    if c.settings.stage in (Stage.LOCAL, Stage.BETA) and c.index.count() == 0:
        c.ingestion.ingest_directory(c.settings.knowledge_dir)

    app = FastAPI(title="OpsPilot", version=__version__)
    app.state.container = c

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["x-request-id"] = request_id
        return response

    @app.exception_handler(InvalidRequestError)
    async def invalid_request(_: Request, exc: InvalidRequestError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(DependencyUnavailableError)
    async def unavailable(_: Request, exc: DependencyUnavailableError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"error": str(exc)},
            headers={"retry-after": str(int(exc.retry_after_seconds))},
        )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            stage=c.settings.stage.value,
            indexed_chunks=c.index.count(),
            version=__version__,
        )

    @app.post("/v1/diagnoses", response_model=DiagnosisResponse)
    def create_diagnosis(body: AlertRequest) -> DiagnosisResponse:
        diagnosis = c.diagnosis.diagnose(body.to_domain())
        return DiagnosisResponse.from_domain(diagnosis)

    @app.post("/v1/ingest", response_model=IngestResponse)
    def ingest() -> IngestResponse:
        report = c.ingestion.ingest_directory(c.settings.knowledge_dir)
        return IngestResponse(
            documents=report.documents,
            chunks=report.chunks,
            indexed_total=c.index.count(),
        )

    return app
