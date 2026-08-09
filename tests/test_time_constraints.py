"""Tests for the natural-language time-constraint parsing in utils.

These exercise pure regex/date logic — no network and no API keys required.
"""

from datetime import datetime
from types import SimpleNamespace

from utils import filter_by_year, parse_time_constraint


def _paper(year: int):
    """Minimal stand-in for an arxiv result: only `.published.year` is read."""
    return SimpleNamespace(published=SimpleNamespace(year=year))


def test_no_constraint():
    clean, start, end, desc = parse_time_constraint("transformers for vision")
    assert clean == "transformers for vision"
    assert start is None and end is None
    assert desc == "no time constraint"


def test_after_year():
    clean, start, end, desc = parse_time_constraint("diffusion models after 2020")
    assert start == 2020
    assert end is None
    assert "diffusion models" in clean
    assert desc == "after 2020"


def test_before_year():
    _, start, end, desc = parse_time_constraint("GANs before 2019")
    assert end == 2019
    assert desc == "before 2019"


def test_between_years():
    _, start, end, desc = parse_time_constraint("RL between 2019 and 2022")
    assert start == 2019
    assert end == 2022
    assert desc == "between 2019 and 2022"


def test_last_n_years_is_relative_to_now():
    _, start, end, desc = parse_time_constraint("attention in the last 3 years")
    assert start == datetime.now().year - 3
    assert "last 3 years" in desc


def test_filter_by_year_bounds_are_inclusive():
    papers = [_paper(2018), _paper(2020), _paper(2023)]

    assert [p.published.year for p in filter_by_year(papers, 2020, None)] == [2020, 2023]
    assert [p.published.year for p in filter_by_year(papers, None, 2020)] == [2018, 2020]
    assert [p.published.year for p in filter_by_year(papers, 2020, 2020)] == [2020]
    assert len(filter_by_year(papers, None, None)) == 3
