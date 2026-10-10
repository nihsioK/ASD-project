from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Subject, User
from app.repositories import subject as subject_repo
from app.schemas.subject import SubjectCreate, SubjectOut
from app.security import get_current_user

router = APIRouter(prefix="/subjects", tags=["subjects"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_own_subject(subject_id: int, user: CurrentUser, db: DbSession) -> Subject:
    subject = subject_repo.get_for_owner(db, user.id, subject_id)
    if subject is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject not found")
    return subject


@router.post("", status_code=status.HTTP_201_CREATED)
def create_subject(data: SubjectCreate, user: CurrentUser, db: DbSession) -> SubjectOut:
    return subject_repo.create(db, user.id, data)


@router.get("")
def list_subjects(user: CurrentUser, db: DbSession) -> list[SubjectOut]:
    return subject_repo.list_for_owner(db, user.id)


@router.get("/{subject_id}")
def get_subject(subject: Annotated[Subject, Depends(get_own_subject)]) -> SubjectOut:
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject: Annotated[Subject, Depends(get_own_subject)], db: DbSession
) -> None:
    subject_repo.delete(db, subject)
