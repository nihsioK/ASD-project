from conftest import auth_headers

CREDS = {"email": "teacher@school.kz", "password": "secret123"}


def test_register_and_login(client):
    r = client.post("/auth/register", json=CREDS)
    assert r.status_code == 201
    assert r.json()["email"] == CREDS["email"]
    assert "password" not in r.text

    r = client.post("/auth/login", json=CREDS)
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_register_duplicate_email(client):
    client.post("/auth/register", json=CREDS)
    assert client.post("/auth/register", json=CREDS).status_code == 409


def test_login_wrong_password(client):
    client.post("/auth/register", json=CREDS)
    r = client.post("/auth/login", json={**CREDS, "password": "wrong-password"})
    assert r.status_code == 401


def test_me(client):
    r = client.get("/auth/me", headers=auth_headers(client))
    assert r.json()["email"] == CREDS["email"]


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401
    assert (
        client.get("/auth/me", headers={"Authorization": "Bearer bad"}).status_code
        == 401
    )
