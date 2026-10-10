from fastapi import APIRouter, status

from app.dependencies import CurrentUser, DbSession, OwnStudent
from app.repositories import student as student_repo
from app.schemas.student import StudentCreate, StudentOut, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, user: CurrentUser, db: DbSession) -> StudentOut:
    return student_repo.create(db, user.id, data)


@router.get("")
def list_students(user: CurrentUser, db: DbSession) -> list[StudentOut]:
    return student_repo.list_for_owner(db, user.id)


@router.get("/{student_id}")
def get_student(student: OwnStudent) -> StudentOut:
    return student


@router.patch("/{student_id}")
def update_student(
    data: StudentUpdate, student: OwnStudent, db: DbSession
) -> StudentOut:
    return student_repo.update(db, student, data)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student: OwnStudent, db: DbSession) -> None:
    student_repo.delete(db, student)
