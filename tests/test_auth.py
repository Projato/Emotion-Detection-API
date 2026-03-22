from fastapi.testclient import TestClient
import pytest

import src.main as main_module
from src.api.dependencies.auth import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)


@pytest.fixture
def client(monkeypatch):
    async def _noop():
        return None

    monkeypatch.setattr(main_module, "connect_to_mongo", _noop)
    monkeypatch.setattr(main_module, "close_mongo_connection", _noop)

    with TestClient(main_module.app) as test_client:
        yield test_client


def test_auth_ping(client):
    response = client.get("/api/v1/auth/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "Auth router is working."}


def test_hash_and_verify_password():
    password = "secret123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpass", hashed) is False


def test_create_and_verify_access_token():
    token = create_access_token({"sub": "testuser"})
    payload = verify_access_token(token)

    assert payload["sub"] == "testuser"
    assert "exp" in payload