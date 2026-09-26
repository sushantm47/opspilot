"""HTTP contract tests. Skipped automatically if FastAPI isn't installed."""

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from opspilot.api.app import create_app  # noqa: E402
from opspilot.domain.errors import DependencyUnavailableError  # noqa: E402

BODY = {
    "alert_id": "api-1",
    "service": "checkout-api",
    "title": "p99 latency above 2s and 5xx errors rising",
}


@pytest.fixture
def client(make_container):
    return TestClient(create_app(make_container()))


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["indexed_chunks"] > 0


def test_diagnose_returns_grounded_answer_and_request_id(client):
    r = client.post("/v1/diagnoses", json=BODY, headers={"x-request-id": "req-123"})
    assert r.status_code == 200
    body = r.json()
    assert body["grounded"] and body["citations"]
    assert r.headers["x-request-id"] == "req-123"


@pytest.mark.parametrize(
    "patch",
    [{"service": "Checkout API!"}, {"title": ""}, {"severity": "SEV9"}],
)
def test_request_validation(client, patch):
    assert client.post("/v1/diagnoses", json={**BODY, **patch}).status_code == 422


def test_open_circuit_maps_to_503_with_retry_after(make_container):
    container = make_container()

    def unavailable(alert, use_cache=True):
        raise DependencyUnavailableError("claude", 12)

    container.diagnosis.diagnose = unavailable
    r = TestClient(create_app(container)).post("/v1/diagnoses", json=BODY)
    assert r.status_code == 503 and r.headers["retry-after"] == "12"
