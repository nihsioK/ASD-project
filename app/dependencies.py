from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Student, Subject, User
from app.repositories import student as student_repo
from app.repositories import subject as subject_repo
from app.security import get_current_user

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_own_subject(subject_id: int, user: CurrentUser, db: DbSession) -> Subject:
    subject = subject_repo.get_for_owner(db, user.id, subject_id)
    if subject is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject not found")
    return subject


def get_own_student(student_id: int, user: CurrentUser, db: DbSession) -> Student:
    student = student_repo.get_for_owner(db, user.id, student_id)
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    return student


OwnSubject = Annotated[Subject, Depends(get_own_subject)]
OwnStudent = Annotated[Student, Depends(get_own_student)]
