from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LessonPlan


def create(db: Session, plan: LessonPlan) -> LessonPlan:
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_for_subject(db: Session, subject_id: int) -> list[LessonPlan]:
    query = (
        select(LessonPlan)
        .where(LessonPlan.subject_id == subject_id)
        .order_by(LessonPlan.id.desc())
    )
    return list(db.scalars(query))


def get_for_subject(db: Session, subject_id: int, plan_id: int) -> LessonPlan | None:
    query = select(LessonPlan).where(
        LessonPlan.id == plan_id, LessonPlan.subject_id == subject_id
    )
    return db.scalar(query)


def delete(db: Session, plan: LessonPlan) -> None:
    db.delete(plan)
    db.commit()
