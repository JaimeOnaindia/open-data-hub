"""Helpers compartidos para tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(relative_path: str) -> Any:
    """Lee un fixture JSON desde tests/fixtures/."""
    path = FIXTURES_DIR / relative_path
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def ine_crime_25997() -> list[dict[str, Any]]:
    return load_fixture("ine/crime_offenses_by_type_25997.json")


@pytest.fixture
def ine_crime_25998() -> list[dict[str, Any]]:
    return load_fixture("ine/crime_offenses_by_sex_25998.json")


@pytest.fixture
def ine_prices_50902() -> list[dict[str, Any]]:
    return load_fixture("ine/consumer_prices_50902.json")


@pytest.fixture
def eurostat_unemployment() -> dict[str, Any]:
    return load_fixture("eurostat/unemployment_une_rt_a.json")


@pytest.fixture
def eurostat_hicp() -> dict[str, Any]:
    return load_fixture("eurostat/hicp_prc_hicp_aind.json")
