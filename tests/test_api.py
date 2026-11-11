from chronorec_demo.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_liveness() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness() -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_failure_is_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("LAB_NOT_READY", "true")
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["detail"] == "Intentional lab readiness failure"


def test_demo_data_is_explicitly_synthetic() -> None:
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["dataset"] == "synthetic-demo-v1"
    assert "no personal or medical data" in body["privacy_notice"]
    assert body["entries"] == 3


def test_entries_limit() -> None:
    response = client.get("/api/v1/entries", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_metrics_are_exposed() -> None:
    client.get("/healthz")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "chronorec_http_requests_total" in response.text
