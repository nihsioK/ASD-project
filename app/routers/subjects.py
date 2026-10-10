from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DbSession, OwnSubject
from app.repositories import subject as subject_repo
from app.schemas.stats import SubjectStats
from app.schemas.subject import SubjectCreate, SubjectOut, SubjectUpdate
from app.services import statistics

router = APIRouter(prefix="/subjects", tags=["subjects"])

DUPLICATE = "Subject with this name and grade already exists"


@router.post("", status_code=status.HTTP_201_CREATED)
def create_subject(data: SubjectCreate, user: CurrentUser, db: DbSession) -> SubjectOut:
    if subject_repo.find_duplicate(db, user.id, data.name, data.grade):
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE)
    return subject_repo.create(db, user.id, data)


@router.get("")
def list_subjects(user: CurrentUser, db: DbSession) -> list[SubjectOut]:
    return subject_repo.list_for_owner(db, user.id)


@router.get("/{subject_id}")
def get_subject(subject: OwnSubject) -> SubjectOut:
    return subject


@router.patch("/{subject_id}")
def update_subject(
    data: SubjectUpdate, subject: OwnSubject, user: CurrentUser, db: DbSession
) -> SubjectOut:
    name = data.name or subject.name
    grade = data.grade or subject.grade
    if subject_repo.find_duplicate(db, user.id, name, grade, exclude_id=subject.id):
        raise HTTPException(status.HTTP_409_CONFLICT, DUPLICATE)
    return subject_repo.update(db, subject, data)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject: OwnSubject, db: DbSession) -> None:
    subject_repo.delete(db, subject)


@router.get("/{subject_id}/stats")
def subject_stats(subject: OwnSubject) -> SubjectStats:
    values = [score.value for score in subject.scores]
    if len(values) < 2:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "At least two scores are required"
        )
    return SubjectStats(
        summary=statistics.summarize(values),
        marks=statistics.mark_distribution(values),
        pass_rate=statistics.pass_rate(values),
    )
