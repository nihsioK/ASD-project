from pydantic import BaseModel, Field


class Measurements(BaseModel):
    values: list[float] = Field(min_length=2, examples=[[9.8, 9.7, 9.9, 9.81]])


class Summary(BaseModel):
    count: int
    mean: float
    median: float
    stdev: float
    min: float
    max: float


class SubjectStats(BaseModel):
    summary: Summary
    marks: dict[int, int] = Field(description="Number of students per mark 5, 4, 3, 2")
    pass_rate: float = Field(description="Share of students with mark 3 or higher")
