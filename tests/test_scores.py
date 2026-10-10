from conftest import auth_headers, create_student, create_subject


def add_score(client, headers, subject_id, student_id, value):
    return client.post(
        f"/subjects/{subject_id}/scores",
        json={"student_id": student_id, "value": value},
        headers=headers,
    )


def test_add_list_delete_scores(client):
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    student_id = create_student(client, headers)

    r = add_score(client, headers, sid, student_id, 92)
    assert r.status_code == 201
    score = r.json()
    assert score == {
        "id": score["id"],
        "student_id": student_id,
        "student_name": "Aruzhan Serikova",
        "value": 92,
        "mark": 5,
    }

    assert client.get(f"/subjects/{sid}/scores", headers=headers).json() == [score]

    url = f"/subjects/{sid}/scores/{score['id']}"
    assert client.delete(url, headers=headers).status_code == 204
    assert client.delete(url, headers=headers).status_code == 404
    assert client.get(f"/subjects/{sid}/scores", headers=headers).json() == []


def test_score_must_be_percent(client):
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    student_id = create_student(client, headers)
    for value in (-1, 101):
        assert add_score(client, headers, sid, student_id, value).status_code == 422


def test_score_requires_own_student(client):
    owner = auth_headers(client, "a@school.kz")
    other = auth_headers(client, "b@school.kz")
    sid = create_subject(client, owner)
    foreign_student = create_student(client, other)

    assert add_score(client, owner, sid, foreign_student, 50).status_code == 404
    assert add_score(client, owner, sid, 9999, 50).status_code == 404


def test_scores_of_other_users_subject_are_hidden(client):
    owner = auth_headers(client, "a@school.kz")
    other = auth_headers(client, "b@school.kz")
    sid = create_subject(client, owner)
    student_id = create_student(client, other)

    assert client.get(f"/subjects/{sid}/scores", headers=other).status_code == 404
    assert add_score(client, other, sid, student_id, 50).status_code == 404


def test_subject_stats(client):
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    for name, value in [("A", 95), ("B", 70), ("C", 55), ("D", 30)]:
        add_score(client, headers, sid, create_student(client, headers, name), value)

    r = client.get(f"/subjects/{sid}/stats", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["count"] == 4
    assert body["summary"]["mean"] == 62.5
    assert body["summary"]["median"] == 62.5
    assert body["marks"] == {"5": 1, "4": 1, "3": 1, "2": 1}
    assert body["pass_rate"] == 0.75


def test_subject_stats_needs_two_scores(client):
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    add_score(client, headers, sid, create_student(client, headers), 80)
    assert client.get(f"/subjects/{sid}/stats", headers=headers).status_code == 400


def test_deleting_subject_deletes_its_scores(client):
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    add_score(client, headers, sid, create_student(client, headers), 80)
    assert client.delete(f"/subjects/{sid}", headers=headers).status_code == 204

    new_sid = create_subject(client, headers, name="Chemistry")
    assert client.get(f"/subjects/{new_sid}/scores", headers=headers).json() == []


def test_deleting_student_deletes_their_scores(client):
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    keep = create_student(client, headers, "Keep")
    remove = create_student(client, headers, "Remove")
    add_score(client, headers, sid, keep, 70)
    add_score(client, headers, sid, remove, 40)

    assert client.delete(f"/students/{remove}", headers=headers).status_code == 204
    scores = client.get(f"/subjects/{sid}/scores", headers=headers).json()
    assert [s["student_name"] for s in scores] == ["Keep"]
