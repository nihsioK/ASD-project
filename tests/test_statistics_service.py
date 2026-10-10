import pytest

from app.services.statistics import mark_distribution, pass_rate, summarize, to_mark


def test_summarize():
    s = summarize([2, 4, 4, 4, 5, 5, 7, 9])
    assert s.count == 8
    assert s.mean == 5
    assert s.median == 4.5
    assert round(s.stdev, 4) == 2.1381
    assert (s.min, s.max) == (2, 9)


def test_summarize_needs_two_values():
    with pytest.raises(ValueError):
        summarize([1])


@pytest.mark.parametrize(
    ("percent", "mark"),
    [(100, 5), (85, 5), (84.9, 4), (65, 4), (64.9, 3), (40, 3), (39.9, 2), (0, 2)],
)
def test_to_mark_boundaries(percent, mark):
    assert to_mark(percent) == mark


def test_mark_distribution():
    assert mark_distribution([90, 70, 66, 50, 10]) == {5: 1, 4: 2, 3: 1, 2: 1}
    assert mark_distribution([]) == {5: 0, 4: 0, 3: 0, 2: 0}


def test_pass_rate():
    assert pass_rate([90, 50, 30, 20]) == 0.5
    assert pass_rate([2 / 3 * 100, 10, 10]) == 0.3333
    assert pass_rate([]) == 0.0
