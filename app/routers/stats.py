import statistics

from fastapi import APIRouter

from app.schemas.stats import Measurements, Summary

router = APIRouter(tags=["stats"])


@router.post("/stats")
def stats(data: Measurements) -> Summary:
    v = data.values
    return Summary(
        count=len(v),
        mean=statistics.fmean(v),
        median=statistics.median(v),
        stdev=statistics.stdev(v),
        min=min(v),
        max=max(v),
    )
