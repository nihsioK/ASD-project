from conftest import auth_headers, create_student

STUDENT = {
    "full_name": "Dias Nurlanov",
    "class_name": "9B",
    "parent_phone": "+7 702 222 3344",
    "notes": "Likes robotics",
}


def test_student_crud(client):
    headers = auth_headers(client)

    r = client.post("/students", json=STUDENT, headers=headers)
    assert r.status_code == 201
    student = r.json()
    assert student == {"id": student["id"], **STUDENT}

    assert client.get("/students", headers=headers).json() == [student]
    url = f"/students/{student['id']}"
    assert client.get(url, headers=headers).json() == student

    r = client.patch(url, json={"class_name": "10B", "notes": None}, headers=headers)
    assert r.json()["class_name"] == "10B"
    assert r.json()["notes"] is None

    r = client.patch(url, json={"full_name": None}, headers=headers)
    assert r.json()["full_name"] == STUDENT["full_name"]

    assert client.delete(url, headers=headers).status_code == 204
    assert client.get(url, headers=headers).status_code == 404


def test_students_sorted_by_class_then_name(client):
    headers = auth_headers(client)
    create_student(client, headers, "Zhanna", "9A")
    create_student(client, headers, "Bolat", "9B")
    create_student(client, headers, "Aidos", "9A")
    names = [s["full_name"] for s in client.get("/students", headers=headers).json()]
    assert names == ["Aidos", "Zhanna", "Bolat"]


def test_student_validation(client):
    headers = auth_headers(client)
    r = client.post(
        "/students", json={"full_name": "", "class_name": "9A"}, headers=headers
    )
    assert r.status_code == 422


def test_students_are_private_to_owner(client):
    owner = auth_headers(client, "a@school.kz")
    other = auth_headers(client, "b@school.kz")
    student_id = create_student(client, owner)

    assert client.get("/students", headers=other).json() == []
    assert client.get(f"/students/{student_id}", headers=other).status_code == 404
    assert client.delete(f"/students/{student_id}", headers=other).status_code == 404
