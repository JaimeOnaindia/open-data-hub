"""Tests de la capa analítica DuckDB (relacionar fuentes por ISO)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from open_data_hub.analytics import relate_eu_indicators, relate_unemployment_sources
from open_data_hub.core import storage


def test_relate_empty_when_no_snapshots(tmp_path: Path) -> None:
    out = relate_eu_indicators(base=tmp_path)
    assert out.empty
    assert list(out.columns) == ["iso", "country", "year", "unemployment", "hicp"]


def test_relate_joins_unemployment_and_prices_by_iso_year(tmp_path: Path) -> None:
    unemployment = pd.DataFrame(
        {
            "country": ["Spain", "Germany", "European Union"],
            "iso": ["ES", "DE", None],
            "year": [2024, 2024, 2024],
            "value": [11.4, 3.4, 6.0],
        }
    )
    hicp = pd.DataFrame(
        {
            "country": ["Spain", "Germany"],
            "iso": ["ES", "DE"],
            "year": [2024, 2024],
            "value": [2.9, 2.5],
        }
    )
    storage.write_view("eu", "labor", "unemployment-rate", unemployment, base=tmp_path)
    storage.write_view("eu", "prices", "hicp-annual", hicp, base=tmp_path)

    out = relate_eu_indicators(base=tmp_path)

    # agregado (iso None) descartado; solo países con ambos indicadores
    assert set(out["iso"]) == {"ES", "DE"}
    spain = out[out["iso"] == "ES"].iloc[0]
    assert spain["unemployment"] == 11.4
    assert spain["hicp"] == 2.9


def test_relate_unemployment_across_sources(tmp_path: Path) -> None:
    eurostat = pd.DataFrame(
        {"country": ["Spain"], "iso": ["ES"], "year": [2023], "value": [12.2]}
    )
    world_bank = pd.DataFrame(
        {"country": ["Spain"], "iso": ["ES"], "year": [2023], "value": [12.18]}
    )
    storage.write_view("eu", "labor", "unemployment-rate", eurostat, base=tmp_path)
    storage.write_view("wb", "labor", "unemployment-rate", world_bank, base=tmp_path)

    out = relate_unemployment_sources(base=tmp_path)

    assert list(out.columns) == ["iso", "year", "eurostat", "world_bank"]
    row = out[(out["iso"] == "ES") & (out["year"] == 2023)].iloc[0]
    assert row["eurostat"] == 12.2
    assert row["world_bank"] == 12.18
