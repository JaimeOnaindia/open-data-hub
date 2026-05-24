"""Tests del cliente Eurostat (JSON-stat 2.0) y sus datasets multi-país."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from open_data_hub.countries.eu.sources.eurostat_client import (
    EurostatClient,
    parse_jsonstat,
)
from open_data_hub.countries.eu.sources.eurostat_datasets import (
    fetch_hicp,
    fetch_unemployment,
)

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def test_parse_jsonstat_dict_index_and_value() -> None:
    payload = {
        "id": ["geo", "time"],
        "size": [2, 2],
        "dimension": {
            "geo": {
                "category": {
                    "index": {"ES": 0, "DE": 1},
                    "label": {"ES": "Spain", "DE": "Germany"},
                }
            },
            "time": {"category": {"index": {"2023": 0, "2024": 1}}},
        },
        # flat 0 = (ES, 2023); flat 3 = (DE, 2024)
        "value": {"0": 12.0, "3": 3.5},
    }
    df = parse_jsonstat(payload)
    assert set(df.columns) == {"geo", "period", "year", "value"}
    spain = df[(df["geo"] == "Spain") & (df["year"] == 2023)]
    assert spain["value"].iloc[0] == 12.0
    germany = df[(df["geo"] == "Germany") & (df["year"] == 2024)]
    assert germany["value"].iloc[0] == 3.5


def test_parse_jsonstat_list_index_and_values_with_nulls() -> None:
    # PxStat/algunas fuentes usan index en forma de lista y value como array con nulls.
    payload = {
        "id": ["geo", "time"],
        "size": [2, 2],
        "dimension": {
            "geo": {"category": {"index": ["ES", "DE"], "label": {"ES": "Spain", "DE": "Germany"}}},
            "time": {"category": {"index": ["2023", "2024"]}},
        },
        "value": [12.0, None, None, 3.5],
    }
    df = parse_jsonstat(payload)
    assert len(df) == 2
    assert set(zip(df["geo"], df["year"], strict=True)) == {("Spain", 2023), ("Germany", 2024)}


def test_parse_jsonstat_extracts_year_from_monthly_period() -> None:
    payload = {
        "id": ["time"],
        "size": [1],
        "dimension": {"time": {"category": {"index": {"2024-03": 0}}}},
        "value": {"0": 2.7},
    }
    df = parse_jsonstat(payload)
    assert df["year"].iloc[0] == 2024
    assert df["period"].iloc[0] == "2024-03"


def test_parse_jsonstat_empty_payload() -> None:
    assert parse_jsonstat({"value": {}}).empty


def test_parse_jsonstat_emits_code_for_code_dims() -> None:
    payload = {
        "id": ["geo", "time"],
        "size": [2, 1],
        "dimension": {
            "geo": {
                "category": {
                    "index": {"ES": 0, "DE": 1},
                    "label": {"ES": "Spain", "DE": "Germany"},
                }
            },
            "time": {"category": {"index": {"2024": 0}}},
        },
        "value": {"0": 1.0, "1": 2.0},
    }
    df = parse_jsonstat(payload, code_dims=("geo",))
    assert {"geo", "geo__code"} <= set(df.columns)
    spain = df[df["geo"] == "Spain"].iloc[0]
    assert spain["geo__code"] == "ES"


@respx.mock
def test_get_dataset_parses_real_fixture(eurostat_unemployment: dict[str, Any]) -> None:
    respx.get(f"{BASE}/une_rt_a").mock(
        return_value=httpx.Response(200, json=eurostat_unemployment)
    )
    with EurostatClient() as client:
        df = client.get_dataset_df("une_rt_a", params={"sex": "T"})

    assert {"geo", "year", "value"} <= set(df.columns)
    assert (df["geo"] == "Spain").any()
    assert df["year"].min() >= 2000


@respx.mock
def test_get_dataset_raises_on_non_jsonstat() -> None:
    respx.get(f"{BASE}/bad").mock(return_value=httpx.Response(200, json={"oops": 1}))
    with EurostatClient() as client, pytest.raises(ValueError, match="JSON-stat"):
        client.get_dataset("bad", params={})


@respx.mock
def test_get_dataset_retries_on_http_error(eurostat_hicp: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/prc_hicp_aind").mock(
        side_effect=[httpx.Response(502), httpx.Response(200, json=eurostat_hicp)]
    )
    with EurostatClient() as client:
        payload = client.get_dataset("prc_hicp_aind", params={})
    assert "value" in payload
    assert route.call_count == 2


@respx.mock
def test_fetch_unemployment_renames_geo_to_country(
    eurostat_unemployment: dict[str, Any],
) -> None:
    respx.get(f"{BASE}/une_rt_a").mock(
        return_value=httpx.Response(200, json=eurostat_unemployment)
    )
    df = fetch_unemployment(nult=6)
    assert list(df.columns) == ["country", "iso", "year", "value"]
    assert (df["country"] == "Spain").any()
    assert df.loc[df["country"] == "Spain", "iso"].iloc[0] == "ES"


@respx.mock
def test_fetch_hicp_returns_tidy(eurostat_hicp: dict[str, Any]) -> None:
    respx.get(f"{BASE}/prc_hicp_aind").mock(
        return_value=httpx.Response(200, json=eurostat_hicp)
    )
    df = fetch_hicp(nult=6)
    assert list(df.columns) == ["country", "iso", "year", "value"]
    assert len(df) > 0
