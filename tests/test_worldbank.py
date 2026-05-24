"""Tests del cliente del Banco Mundial y sus datasets."""

from __future__ import annotations

from typing import Any

import httpx
import respx

from open_data_hub.countries.wb.sources.worldbank_client import WorldBankClient
from open_data_hub.countries.wb.sources.worldbank_datasets import fetch_unemployment

BASE = "https://api.worldbank.org/v2"
UNEMPLOYMENT = f"{BASE}/country/all/indicator/SL.UEM.TOTL.ZS"


@respx.mock
def test_get_indicator_df_keeps_countries_drops_aggregates(
    worldbank_unemployment: list[Any],
) -> None:
    respx.get(UNEMPLOYMENT).mock(return_value=httpx.Response(200, json=worldbank_unemployment))
    with WorldBankClient() as client:
        df = client.get_indicator_df("SL.UEM.TOTL.ZS")

    assert list(df.columns) == ["country", "iso", "year", "value"]
    # ES/DE/FR conservados; agregados 1W (World) y EU descartados
    assert set(df["iso"]) == {"ES", "DE", "FR"}
    spain_2023 = df[(df["iso"] == "ES") & (df["year"] == 2023)]
    assert abs(spain_2023["value"].iloc[0] - 12.179) < 0.001


@respx.mock
def test_fetch_unemployment_returns_tidy(worldbank_unemployment: list[Any]) -> None:
    respx.get(UNEMPLOYMENT).mock(return_value=httpx.Response(200, json=worldbank_unemployment))
    df = fetch_unemployment(nult=5)
    assert list(df.columns) == ["country", "iso", "year", "value"]
    assert (df["iso"] == "ES").any()


@respx.mock
def test_get_indicator_paginates() -> None:
    page1 = [
        {"page": 1, "pages": 2, "per_page": 1, "total": 2},
        [{"country": {"id": "ES", "value": "Spain"}, "date": "2023", "value": 11.0}],
    ]
    page2 = [
        {"page": 2, "pages": 2, "per_page": 1, "total": 2},
        [{"country": {"id": "DE", "value": "Germany"}, "date": "2023", "value": 3.0}],
    ]
    route = respx.get(f"{BASE}/country/all/indicator/X").mock(
        side_effect=[httpx.Response(200, json=page1), httpx.Response(200, json=page2)]
    )
    with WorldBankClient() as client:
        rows = client.get_indicator("X")

    assert route.call_count == 2
    assert {r["country"]["id"] for r in rows} == {"ES", "DE"}


@respx.mock
def test_get_indicator_raises_on_short_payload() -> None:
    respx.get(f"{BASE}/country/all/indicator/Y").mock(
        return_value=httpx.Response(200, json=[{"message": "no data"}])
    )
    with WorldBankClient() as client:
        try:
            client.get_indicator("Y")
        except ValueError as exc:
            assert "Banco Mundial" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("debería lanzar ValueError")
