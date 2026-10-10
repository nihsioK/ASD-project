from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DbSession, OwnSubject
from app.repositories import score as score_repo
from app.repositories import student as student_repo
from app.schemas.score import ScoreCreate, ScoreOut

router = APIRouter(prefix="/subjects/{subject_id}/scores", tags=["scores"])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_score(
    data: ScoreCreate, subject: OwnSubject, user: CurrentUser, db: DbSession
) -> ScoreOut:
    if student_repo.get_for_owner(db, user.id, data.student_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    return score_repo.create(db, subject.id, data)


@router.get("")
def list_scores(subject: OwnSubject, db: DbSession) -> list[ScoreOut]:
    return score_repo.list_for_subject(db, subject.id)


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_score(score_id: int, subject: OwnSubject, db: DbSession) -> None:
    score = score_repo.get_for_subject(db, subject.id, score_id)
    if score is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Score not found")
    score_repo.delete(db, score)
