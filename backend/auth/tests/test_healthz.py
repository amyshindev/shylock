from fastapi.testclient import TestClient

from auth_main import app


def test_healthz() -> None:
    client = TestClient(app)
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"ok": True}
