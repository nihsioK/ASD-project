from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    value: Mapped[float]

    student: Mapped["Student"] = relationship(back_populates="scores")  # noqa: F821

    @property
    def student_name(self) -> str:
        return self.student.full_name
