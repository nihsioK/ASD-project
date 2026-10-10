from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    grade: Mapped[int]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
