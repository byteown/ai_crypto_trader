import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_session():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)
