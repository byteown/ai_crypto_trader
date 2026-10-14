from sqlalchemy.exc import InterfaceError

from app.db.session import get_session
from app.main import app


class FakeSession:
    async def execute(self, stmt):
        return None


class BrokenSession:
    async def execute(self, stmt):
        raise InterfaceError("", "", "")


def test_health_ok(client):
    app.dependency_overrides[get_session] = lambda: FakeSession()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}


def test_health_db_down(client):
    app.dependency_overrides[get_session] = lambda: BrokenSession()
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "error", "db": "unavailable"}
