from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("owner_id", "name", "grade"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    grade: Mapped[int]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    scores: Mapped[list["Score"]] = relationship(  # noqa: F821
        cascade="all, delete-orphan", order_by="Score.id"
    )
    plans: Mapped[list["LessonPlan"]] = relationship(  # noqa: F821
        cascade="all, delete-orphan"
    )
