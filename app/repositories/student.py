from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Student
from app.schemas.student import StudentCreate, StudentUpdate


def create(db: Session, owner_id: int, data: StudentCreate) -> Student:
    student = Student(owner_id=owner_id, **data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def list_for_owner(db: Session, owner_id: int) -> list[Student]:
    query = (
        select(Student)
        .where(Student.owner_id == owner_id)
        .order_by(Student.class_name, Student.full_name)
    )
    return list(db.scalars(query))


def get_for_owner(db: Session, owner_id: int, student_id: int) -> Student | None:
    query = select(Student).where(
        Student.id == student_id, Student.owner_id == owner_id
    )
    return db.scalar(query)


def update(db: Session, student: Student, data: StudentUpdate) -> Student:
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None and field in ("full_name", "class_name"):
            continue  # required columns can't be cleared
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


def delete(db: Session, student: Student) -> None:
    db.delete(student)
    db.commit()
