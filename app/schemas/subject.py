from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Physics"])
    grade: int = Field(ge=1, le=11, examples=[9])


class SubjectOut(SubjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
