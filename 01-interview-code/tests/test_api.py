import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CHRONICLE_DB", str(tmp_path / "test.db"))
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_patients_empty(client):
    response = client.get("/patients")
    assert response.status_code == 200
    assert response.json() == []


def test_timeline_unknown_patient(client):
    response = client.get("/patients/P-999/timeline")
    assert response.status_code == 404
