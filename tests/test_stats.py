def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_stats(client):
    r = client.post("/stats", json={"values": [1, 2, 3, 4]})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 4
    assert body["mean"] == 2.5
    assert body["median"] == 2.5
    assert round(body["stdev"], 4) == 1.291
    assert (body["min"], body["max"]) == (1, 4)


def test_stats_rejects_too_few_values(client):
    assert client.post("/stats", json={"values": [1]}).status_code == 422
