from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Score
from app.schemas.score import ScoreCreate


def create(db: Session, subject_id: int, data: ScoreCreate) -> Score:
    score = Score(subject_id=subject_id, **data.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


def list_for_subject(db: Session, subject_id: int) -> list[Score]:
    query = (
        select(Score)
        .where(Score.subject_id == subject_id)
        .options(selectinload(Score.student))
        .order_by(Score.id)
    )
    return list(db.scalars(query))


def get_for_subject(db: Session, subject_id: int, score_id: int) -> Score | None:
    query = select(Score).where(Score.id == score_id, Score.subject_id == subject_id)
    return db.scalar(query)


def delete(db: Session, score: Score) -> None:
    db.delete(score)
    db.commit()
