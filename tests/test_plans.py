from conftest import auth_headers, create_subject

from app.services import ai


def test_generate_plan_with_mock(client, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    headers = auth_headers(client)
    sid = create_subject(client, headers)

    r = client.post(
        f"/subjects/{sid}/plans",
        json={"topic": "Newton's second law", "objectives": "Apply F = ma"},
        headers=headers,
    )
    assert r.status_code == 201
    plan = r.json()
    assert plan["source"] == "mock"
    assert plan["subject_id"] == sid
    assert "# Short-term plan: Newton's second law" in plan["content"]
    assert "Apply F = ma" in plan["content"]
    assert "Grade: 9" in plan["content"]

    plans = client.get(f"/subjects/{sid}/plans", headers=headers).json()
    assert [p["id"] for p in plans] == [plan["id"]]

    url = f"/subjects/{sid}/plans/{plan['id']}"
    assert client.delete(url, headers=headers).status_code == 204
    assert client.delete(url, headers=headers).status_code == 404


def test_plan_topic_is_required(client):
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    r = client.post(f"/subjects/{sid}/plans", json={"topic": ""}, headers=headers)
    assert r.status_code == 422


def test_plans_of_other_users_subject_are_hidden(client):
    owner = auth_headers(client, "a@school.kz")
    other = auth_headers(client, "b@school.kz")
    sid = create_subject(client, owner)
    r = client.post(f"/subjects/{sid}/plans", json={"topic": "Atoms"}, headers=other)
    assert r.status_code == 404


def test_ai_failure_returns_502(client, monkeypatch):
    def fail(*args):
        raise ai.AIServiceError("OpenRouter request failed: timeout")

    monkeypatch.setattr(ai, "generate_plan", fail)
    headers = auth_headers(client)
    sid = create_subject(client, headers)
    r = client.post(f"/subjects/{sid}/plans", json={"topic": "Atoms"}, headers=headers)
    assert r.status_code == 502
    assert "timeout" in r.json()["detail"]
