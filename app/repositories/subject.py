from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


def create(db: Session, owner_id: int, data: SubjectCreate) -> Subject:
    subject = Subject(owner_id=owner_id, **data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def list_for_owner(db: Session, owner_id: int) -> list[Subject]:
    query = select(Subject).where(Subject.owner_id == owner_id).order_by(Subject.id)
    return list(db.scalars(query))


def get_for_owner(db: Session, owner_id: int, subject_id: int) -> Subject | None:
    query = select(Subject).where(
        Subject.id == subject_id, Subject.owner_id == owner_id
    )
    return db.scalar(query)


def find_duplicate(
    db: Session, owner_id: int, name: str, grade: int, exclude_id: int | None = None
) -> Subject | None:
    query = select(Subject).where(
        Subject.owner_id == owner_id, Subject.name == name, Subject.grade == grade
    )
    if exclude_id is not None:
        query = query.where(Subject.id != exclude_id)
    return db.scalar(query)


def update(db: Session, subject: Subject, data: SubjectUpdate) -> Subject:
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(subject, field, value)
    db.commit()
    db.refresh(subject)
    return subject


def delete(db: Session, subject: Subject) -> None:
    db.delete(subject)
    db.commit()
