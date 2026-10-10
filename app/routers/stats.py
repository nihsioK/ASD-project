from fastapi import APIRouter

from app.schemas.stats import Measurements, Summary
from app.services import statistics

router = APIRouter(tags=["stats"])


@router.post("/stats")
def stats(data: Measurements) -> Summary:
    return statistics.summarize(data.values)
