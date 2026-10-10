from app.models import LessonPlan, Score, Student, Subject
from app.seed import DEMO_EMAIL, DEMO_PASSWORD, seed


def test_seed_creates_demo_data_once(db_session, client):
    with db_session() as db:
        assert seed(db) is True
        assert seed(db) is False
        assert db.query(Student).count() == 8
        assert db.query(Subject).count() == 3
        assert db.query(Score).count() == 24
        assert db.query(LessonPlan).count() == 1

    r = client.post(
        "/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
    )
    assert r.status_code == 200
