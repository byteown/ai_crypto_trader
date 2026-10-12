import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def reset_session():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)
