"""Tests de la capa de almacenamiento parquet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from open_data_hub.core import storage


def test_round_trip(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {"country": ["Spain", "France"], "year": [2024, 2024], "value": [1.0, 2.0]}
    )
    storage.write_view("eu", "labor", "unemployment-rate", df, source="Eurostat", base=tmp_path)
    out = storage.read_view("eu", "labor", "unemployment-rate", base=tmp_path)
    assert out is not None
    pd.testing.assert_frame_equal(out, df)


def test_read_missing_returns_none(tmp_path: Path) -> None:
    assert storage.read_view("xx", "y", "z", base=tmp_path) is None
    assert storage.read_meta("xx", "y", "z", base=tmp_path) is None


def test_meta_records_provenance(tmp_path: Path) -> None:
    df = pd.DataFrame({"year": [2024], "value": [1.0]})
    storage.write_view("es", "crime", "offenses-by-type", df, source="INE", base=tmp_path)
    meta = storage.read_meta("es", "crime", "offenses-by-type", base=tmp_path)
    assert meta is not None
    assert meta["source"] == "INE"
    assert meta["rows"] == 1
    assert meta["view_key"] == "offenses-by-type"
    assert "fetched_at" in meta


def test_view_path_structure(tmp_path: Path) -> None:
    path = storage.view_path("es", "crime", "offenses-by-type", base=tmp_path)
    assert path == tmp_path / "es" / "crime" / "offenses-by-type.parquet"
