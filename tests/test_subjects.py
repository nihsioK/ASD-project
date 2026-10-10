from conftest import auth_headers


def test_subject_crud(client):
    headers = auth_headers(client)

    r = client.post("/subjects", json={"name": "Physics", "grade": 9}, headers=headers)
    assert r.status_code == 201
    subject = r.json()
    assert subject["name"] == "Physics"

    assert client.get("/subjects", headers=headers).json() == [subject]
    assert client.get(f"/subjects/{subject['id']}", headers=headers).json() == subject

    assert (
        client.delete(f"/subjects/{subject['id']}", headers=headers).status_code == 204
    )
    assert client.get(f"/subjects/{subject['id']}", headers=headers).status_code == 404


def test_subject_validation(client):
    headers = auth_headers(client)
    r = client.post("/subjects", json={"name": "Physics", "grade": 12}, headers=headers)
    assert r.status_code == 422


def test_subjects_are_private_to_owner(client):
    owner = auth_headers(client, "a@school.kz")
    other = auth_headers(client, "b@school.kz")
    subject_id = client.post(
        "/subjects", json={"name": "Math", "grade": 5}, headers=owner
    ).json()["id"]

    assert client.get("/subjects", headers=other).json() == []
    assert client.get(f"/subjects/{subject_id}", headers=other).status_code == 404


def test_subjects_require_token(client):
    assert client.get("/subjects").status_code == 401
