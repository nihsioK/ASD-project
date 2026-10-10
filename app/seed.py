"""Fill the database with demo data: python -m app.seed

Idempotent: does nothing if the demo teacher already exists.
"""

from sqlalchemy.orm import Session

from app import models  # noqa: F401 - registers tables on Base.metadata
from app.db import Base, SessionLocal, engine
from app.models import LessonPlan, Score, Student, Subject
from app.repositories import user as user_repo
from app.security import hash_password
from app.services.ai import mock_plan

DEMO_EMAIL = "demo@school.kz"
DEMO_PASSWORD = "demo12345"

STUDENTS = [
    ("Aruzhan Serikova", "9A", "+7 701 111 2233", "Olympiad in physics"),
    ("Dias Nurlanov", "9A", "+7 702 222 3344", None),
    ("Aigerim Bekova", "9A", "+7 705 333 4455", "Needs extra support in math"),
    ("Timur Akhmetov", "9A", "+7 707 444 5566", None),
    ("Madina Zhakupova", "9B", "+7 701 555 6677", "Class monitor"),
    ("Yerlan Sadykov", "9B", "+7 702 666 7788", None),
    ("Kamila Ospanova", "9B", "+7 705 777 8899", None),
    ("Nursultan Abenov", "9B", "+7 707 888 9900", "Often absent on Mondays"),
]

# subject -> percent scores of each student, in STUDENTS order
SCORES = {
    ("Physics", 9): [96, 78, 55, 64, 88, 71, 42, 35],
    ("Mathematics", 9): [91, 85, 38, 67, 79, 58, 73, 49],
    ("Computer Science", 9): [99, 92, 61, 84, 76, 68, 90, 57],
}


def seed(db: Session) -> bool:
    """Create demo data; returns False if it already exists."""
    if user_repo.get_by_email(db, DEMO_EMAIL):
        return False
    teacher = user_repo.create(db, DEMO_EMAIL, hash_password(DEMO_PASSWORD))

    students = [
        Student(
            owner_id=teacher.id,
            full_name=name,
            class_name=class_name,
            parent_phone=phone,
            notes=notes,
        )
        for name, class_name, phone, notes in STUDENTS
    ]
    db.add_all(students)

    subjects = {}
    for (name, grade), values in SCORES.items():
        subjects[name] = Subject(owner_id=teacher.id, name=name, grade=grade)
        subjects[name].scores = [
            Score(student=student, value=value)
            for student, value in zip(students, values, strict=True)
        ]
    db.add_all(subjects.values())

    topic = "Newton's second law"
    subjects["Physics"].plans = [
        LessonPlan(
            topic=topic,
            objectives="9.2.2.4 apply Newton's second law to solve problems",
            content=mock_plan("Physics", 9, topic, None),
            source="mock",
        )
    ]
    db.commit()
    return True


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        created = seed(db)
    print("Demo data created" if created else "Demo data already exists")
    print(f"Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
