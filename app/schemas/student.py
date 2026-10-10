from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150, examples=["Aruzhan Serikova"])
    class_name: str = Field(min_length=1, max_length=10, examples=["9A"])
    parent_phone: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=1000)


class StudentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    class_name: str | None = Field(default=None, min_length=1, max_length=10)
    parent_phone: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=1000)


class StudentOut(StudentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
