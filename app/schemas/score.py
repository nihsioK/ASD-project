from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.services.statistics import to_mark


class ScoreCreate(BaseModel):
    student_id: int
    value: float = Field(ge=0, le=100, description="Percent of the maximum score")


class ScoreOut(ScoreCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_name: str

    @computed_field
    @property
    def mark(self) -> int:
        return to_mark(self.value)
