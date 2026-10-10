"""Pure statistics functions, independent of HTTP and the database."""

import statistics

from app.schemas.stats import Summary

# Criteria-based assessment: percentage of the maximum score -> mark on a 5-point scale
MARK_THRESHOLDS = ((85, 5), (65, 4), (40, 3))
PASS_MARK = 3


def summarize(values: list[float]) -> Summary:
    if len(values) < 2:
        raise ValueError("At least two values are required")
    return Summary(
        count=len(values),
        mean=statistics.fmean(values),
        median=statistics.median(values),
        stdev=statistics.stdev(values),
        min=min(values),
        max=max(values),
    )


def to_mark(percent: float) -> int:
    for threshold, mark in MARK_THRESHOLDS:
        if percent >= threshold:
            return mark
    return 2


def mark_distribution(percents: list[float]) -> dict[int, int]:
    distribution = {5: 0, 4: 0, 3: 0, 2: 0}
    for percent in percents:
        distribution[to_mark(percent)] += 1
    return distribution


def pass_rate(percents: list[float]) -> float:
    if not percents:
        return 0.0
    passed = sum(to_mark(p) >= PASS_MARK for p in percents)
    return round(passed / len(percents), 4)
