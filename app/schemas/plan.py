from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlanCreate(BaseModel):
    topic: str = Field(min_length=3, max_length=200, examples=["Newton's second law"])
    objectives: str | None = Field(default=None, max_length=1000)


class PlanOut(PlanCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    content: str
    source: str
    created_at: datetime
