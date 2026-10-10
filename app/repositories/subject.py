from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subject
from app.schemas.subject import SubjectCreate


def create(db: Session, owner_id: int, data: SubjectCreate) -> Subject:
    subject = Subject(owner_id=owner_id, **data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def list_for_owner(db: Session, owner_id: int) -> list[Subject]:
    return list(
        db.scalars(
            select(Subject).where(Subject.owner_id == owner_id).order_by(Subject.id)
        )
    )


def get_for_owner(db: Session, owner_id: int, subject_id: int) -> Subject | None:
    return db.scalar(
        select(Subject).where(Subject.id == subject_id, Subject.owner_id == owner_id)
    )


def delete(db: Session, subject: Subject) -> None:
    db.delete(subject)
    db.commit()
