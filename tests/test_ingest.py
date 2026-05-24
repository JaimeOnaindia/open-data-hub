"""Tests de ingesta: reutiliza los fetchers y persiste a parquet."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
import respx

from open_data_hub.core import storage
from open_data_hub.ingest import ingest_all, ingest_view

BASE = "https://servicios.ine.es/wstempus/js/ES"


@respx.mock
def test_ingest_view_persists_and_records_source(
    tmp_path: Path, ine_crime_25997: list[dict[str, Any]]
) -> None:
    respx.get(f"{BASE}/DATOS_TABLA/25997").mock(
        return_value=httpx.Response(200, json=ine_crime_25997)
    )
    rows = ingest_view("es", "crime", "offenses-by-type", nult=5, base=tmp_path)
    assert rows > 0

    df = storage.read_view("es", "crime", "offenses-by-type", base=tmp_path)
    assert df is not None and not df.empty
    assert {"offense_type", "year", "value"} <= set(df.columns)

    meta = storage.read_meta("es", "crime", "offenses-by-type", base=tmp_path)
    assert meta is not None
    assert meta["source"] == "INE"
    assert meta["rows"] == rows


@respx.mock
def test_ingest_all_covers_every_registered_view(tmp_path: Path) -> None:
    # Respuestas vacías de ambas fuentes: nos interesa que TODA vista registrada se ingeste.
    respx.route(host="servicios.ine.es").mock(return_value=httpx.Response(200, json=[]))
    respx.route(host="ec.europa.eu").mock(
        return_value=httpx.Response(
            200, json={"id": [], "size": [], "dimension": {}, "value": {}}
        )
    )

    results = ingest_all(nult=3, base=tmp_path)

    assert len(results) >= 11  # 9 vistas ES + 2 EU
    for country_code, dataset_key, view_key, _rows in results:
        assert storage.read_view(country_code, dataset_key, view_key, base=tmp_path) is not None
        meta = storage.read_meta(country_code, dataset_key, view_key, base=tmp_path)
        assert meta is not None and meta["source"] in {"INE", "Eurostat"}
