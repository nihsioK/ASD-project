import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db, make_engine
from app.main import app

# CI sets TEST_DATABASE_URL to a PostgreSQL service; locally an in-memory SQLite is used
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")


@pytest.fixture
def db_session():
    if TEST_DATABASE_URL == "sqlite://":
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
    else:
        engine = make_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    yield TestSession
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        with db_session() as db:
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


def create_student(client, headers, full_name="Aruzhan Serikova", class_name="9A"):
    r = client.post(
        "/students",
        json={"full_name": full_name, "class_name": class_name},
        headers=headers,
    )
    return r.json()["id"]


def create_subject(client, headers, name="Physics", grade=9):
    r = client.post("/subjects", json={"name": name, "grade": grade}, headers=headers)
    return r.json()["id"]
