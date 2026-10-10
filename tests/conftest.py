import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # fresh in-memory database for every test
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        with TestSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def auth_headers(client, email="teacher@school.kz", password="secret123"):
    client.post("/auth/register", json={"email": email, "password": password})
    token = client.post(
        "/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
