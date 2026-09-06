import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.services import transaction_client

client = TestClient(app)

VALID_PAYLOAD = {
    "endToEndId": "REF20260831001",
    "debtor": {"name": "Acme Exports Ltd"},
    "creditor": {"name": "Example Trading Co"},
    "instructedAmount": {"amount": "1000.00", "currency": "USD"},
}


def test_create_transaction_rejects_missing_api_key():
    response = client.post("/transactions", json=VALID_PAYLOAD)
    assert response.status_code in (401, 422)


def test_create_transaction_rejects_bad_currency_length():
    bad_payload = {**VALID_PAYLOAD, "instructedAmount": {"amount": "1000.00", "currency": "US"}}
    response = client.post(
        "/transactions", json=bad_payload, headers={"x-api-key": "dev-secret-key"}
    )
    assert response.status_code == 422


def test_create_transaction_forwards_transaction_service_success(monkeypatch):
    async def fake_create_transaction(payload):
        return httpx.responseonse(201, json={**payload, "id": "abc-123", "status": "clear"})
    monkeypatch.setattr(transaction_client, "create_transaction", fake_create_transaction)
    response = client.post("/transactions", json=VALID_PAYLOAD, headers={"x-api-key": "dev-secret-key"})
    assert response.status_code == 201
    assert response.json()["id"] == "abc-123"


def test_get_transaction_rejects_missing_api_key():
    response = client.get("/transactions/some-id")
    assert response.status_code in (401, 422)


def test_get_transaction_forwards_not_found(monkeypatch):
    async def fake_get_transaction(transaction_id):
        return httpx.responseonse(
            404,
            json={"error": "not_found", "message": f"transaction {transaction_id} does not exist"},
        )

    monkeypatch.setattr(transaction_client, "get_transaction", fake_get_transaction)

    response = client.get("/transactions/does-not-exist", headers={"x-api-key": "dev-secret-key"})
    assert response.status_code == 404
    assert response.json() == {
        "error": "not_found",
        "message": "transaction does-not-exist does not exist",
    }


def test_create_transaction_returns_502_when_transaction_service_unreachable():
    response = client.post("/transactions", json=VALID_PAYLOAD, headers={"x-api-key": "dev-secret-key"})
    assert response.status_code == 502
    assert response.json() == {"error": "http_error", "message": "transaction service unreachable"}