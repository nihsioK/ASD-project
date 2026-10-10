from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    full_name: Mapped[str]
    class_name: Mapped[str]
    parent_phone: Mapped[str | None]
    notes: Mapped[str | None]

    scores: Mapped[list["Score"]] = relationship(  # noqa: F821
        back_populates="student", cascade="all, delete-orphan"
    )
