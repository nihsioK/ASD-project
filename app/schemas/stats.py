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
