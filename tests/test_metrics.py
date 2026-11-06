import httpx
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from app.main import app
from app.services import transaction_client

client = TestClient(app)
HEADERS = {"x-api-key": "dev-secret-key"}
PAYLOAD = {
    "endToEndId": "REF20260831001",
    "debtor": {"name": "Acme Exports Ltd"},
    "creditor": {"name": "Example Trading Co"},
    "instructedAmount": {"amount": "1000.00", "currency": "USD"},
}
MT103 = ":20:REF1\n:32A:260831USD500,5\n:50K:PAYER\n:59:PAYEE"


def sample(name, **labels):
    # Counters are process-wide, so tests compare before/after instead of absolute values
    return REGISTRY.get_sample_value(name, labels) or 0.0


def fake_backend(monkeypatch):
    async def fake_create(payload):
        return httpx.Response(201, json={**payload, "id": "abc-123", "status": "clear"})

    async def fake_get(transaction_id):
        return httpx.Response(200, json={"id": transaction_id, "status": "clear"})

    monkeypatch.setattr(transaction_client, "create_transaction", fake_create)
    monkeypatch.setattr(transaction_client, "get_transaction", fake_get)


def test_request_is_counted_and_timed_by_route_and_status(monkeypatch):
    fake_backend(monkeypatch)
    labels = {"method": "POST", "route": "/transactions", "status": "201"}
    before = sample("http_requests_total", **labels)
    timed_before = sample("http_request_duration_seconds_count", method="POST", route="/transactions")

    assert client.post("/transactions", json=PAYLOAD, headers=HEADERS).status_code == 201

    assert sample("http_requests_total", **labels) == before + 1
    assert sample("http_request_duration_seconds_count", method="POST", route="/transactions") == timed_before + 1


def test_errors_are_counted_with_their_status():
    labels = {"method": "POST", "route": "/transactions", "status": "422"}
    before = sample("http_requests_total", **labels)
    bad = {**PAYLOAD, "instructedAmount": {"amount": "1000.00", "currency": "US"}}

    assert client.post("/transactions", json=bad, headers=HEADERS).status_code == 422

    assert sample("http_requests_total", **labels) == before + 1


def test_route_label_is_the_template_not_the_raw_path(monkeypatch):
    fake_backend(monkeypatch)
    labels = {"method": "GET", "route": "/transactions/{transaction_id}", "status": "200"}
    before = sample("http_requests_total", **labels)

    client.get("/transactions/id-one", headers=HEADERS)
    client.get("/transactions/id-two", headers=HEADERS)

    assert sample("http_requests_total", **labels) == before + 2
    assert "id-one" not in client.get("/metrics").text


def test_unknown_paths_share_one_label():
    labels = {"method": "GET", "route": "unmatched", "status": "404"}
    before = sample("http_requests_total", **labels)

    client.get("/no-such-path-123")

    assert sample("http_requests_total", **labels) == before + 1
    assert "no-such-path-123" not in client.get("/metrics").text


def test_probes_and_scrapes_are_not_counted():
    client.get("/healthz")
    client.get("/metrics")

    body = client.get("/metrics").text
    assert 'route="/healthz"' not in body
    assert 'route="/metrics"' not in body


def test_transactions_are_counted_by_input_format(monkeypatch):
    fake_backend(monkeypatch)
    iso_before = sample("gateway_transactions_received_total", format="iso20022")
    mt_before = sample("gateway_transactions_received_total", format="mt103")

    client.post("/transactions", json=PAYLOAD, headers=HEADERS)
    client.post("/transactions/mt103", content=MT103, headers=HEADERS)

    assert sample("gateway_transactions_received_total", format="iso20022") == iso_before + 1
    assert sample("gateway_transactions_received_total", format="mt103") == mt_before + 1


def test_metrics_endpoint_serves_prometheus_text_with_the_slo_bucket():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert 'le="0.3"' in response.text  # the SLO threshold must be a bucket boundary
