from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Physics"])
    grade: int = Field(ge=1, le=11, examples=[9])


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    grade: int | None = Field(default=None, ge=1, le=11)


class SubjectOut(SubjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
