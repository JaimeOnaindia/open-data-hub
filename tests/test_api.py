"""Tests de la API FastAPI con TestClient + respx para mockear el INE."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx
import pandas as pd
import pytest
import respx
from fastapi.testclient import TestClient

from open_data_hub.api import _load_dataset_view, app
from open_data_hub.core import storage

BASE = "https://servicios.ine.es/wstempus/js/ES"
EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_view_cache() -> Iterator[None]:
    """El endpoint usa lru_cache; limpiamos entre tests para evitar contaminación."""
    _load_dataset_view.cache_clear()
    yield
    _load_dataset_view.cache_clear()


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_countries_shape(client: TestClient) -> None:
    response = client.get("/api/countries")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    es = next(c for c in payload if c["code"] == "es")
    assert es["name"] == "España"
    assert es["flag"] == "🇪🇸"
    keys = {d["key"] for d in es["datasets"]}
    assert {"crime", "prices", "labor", "demography"} <= keys


def test_list_datasets_is_flat(client: TestClient) -> None:
    response = client.get("/api/datasets")
    assert response.status_code == 200
    payload = response.json()
    required = {"country_code", "country_name", "key", "label"}
    assert all(required <= set(item) for item in payload)
    crime = next(
        item for item in payload if item["country_code"] == "es" and item["key"] == "crime"
    )
    assert crime["source_name"] == "INE"


def test_views_for_known_dataset(client: TestClient) -> None:
    response = client.get("/api/datasets/es/crime/views")
    assert response.status_code == 200
    views = response.json()
    keys = {v["key"] for v in views}
    assert "offenses-by-type" in keys
    assert "offenses-by-sex" in keys


def test_unknown_country_returns_404(client: TestClient) -> None:
    response = client.get("/api/datasets/xx/crime/views")
    assert response.status_code == 404
    assert "País" in response.json()["detail"]


def test_unknown_dataset_returns_404(client: TestClient) -> None:
    response = client.get("/api/datasets/es/unknown/views")
    assert response.status_code == 404
    assert "Dataset" in response.json()["detail"]


def test_unknown_view_returns_404(client: TestClient) -> None:
    response = client.get("/api/datasets/es/crime/views/unknown-view")
    assert response.status_code == 404
    assert "Vista" in response.json()["detail"]


def test_nult_bounds_validated(client: TestClient) -> None:
    too_low = client.get("/api/datasets/es/crime/views/offenses-by-type?nult=1")
    too_high = client.get("/api/datasets/es/crime/views/offenses-by-type?nult=99")
    assert too_low.status_code == 422
    assert too_high.status_code == 422


@respx.mock
def test_get_view_returns_records(
    client: TestClient, ine_crime_25997: list[dict[str, Any]]
) -> None:
    respx.get(f"{BASE}/DATOS_TABLA/25997").mock(
        return_value=httpx.Response(200, json=ine_crime_25997)
    )
    response = client.get("/api/datasets/es/crime/views/offenses-by-type?nult=3")
    assert response.status_code == 200
    payload = response.json()
    assert payload["view"]["key"] == "offenses-by-type"
    assert payload["view"]["category_col"] == "offense_type"
    assert "metric" in payload["view"]["filter_cols"]
    assert len(payload["records"]) > 0
    # servido en vivo (sin snapshot en el dir aislado) → sin fecha de snapshot
    assert payload["fetched_at"] is None

    sample = payload["records"][0]
    assert {"year", "value", "scope", "metric", "offense_type"} <= set(sample.keys())
    assert sample["value"] is None or isinstance(sample["value"], (int, float))


@respx.mock
def test_legacy_crime_endpoints_match_generic(
    client: TestClient, ine_crime_25997: list[dict[str, Any]]
) -> None:
    respx.get(f"{BASE}/DATOS_TABLA/25997").mock(
        return_value=httpx.Response(200, json=ine_crime_25997)
    )
    legacy = client.get("/api/crime/views/offenses-by-type?nult=3")
    assert legacy.status_code == 200
    assert legacy.json()["view"]["key"] == "offenses-by-type"


def test_legacy_list_crime_views(client: TestClient) -> None:
    response = client.get("/api/crime/views")
    assert response.status_code == 200
    keys = {v["key"] for v in response.json()}
    assert "offenses-by-type" in keys


def test_catalog_includes_eurostat_provider(client: TestClient) -> None:
    response = client.get("/api/countries")
    assert response.status_code == 200
    eu = next(c for c in response.json() if c["code"] == "eu")
    assert eu["flag"] == "🇪🇺"
    keys = {d["key"] for d in eu["datasets"]}
    assert {"labor", "prices"} <= keys


def test_catalog_includes_world_bank_provider(client: TestClient) -> None:
    response = client.get("/api/v1/countries")
    wb = next(c for c in response.json() if c["code"] == "wb")
    assert wb["flag"] == "🌍"
    keys = {d["key"] for d in wb["datasets"]}
    assert {"labor", "prices", "economy"} <= keys


@respx.mock
def test_world_bank_view_returns_records(
    client: TestClient, worldbank_unemployment: list[Any]
) -> None:
    respx.get("https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS").mock(
        return_value=httpx.Response(200, json=worldbank_unemployment)
    )
    response = client.get("/api/v1/datasets/wb/labor/views/unemployment-rate?nult=5")
    assert response.status_code == 200
    records = response.json()["records"]
    assert len(records) > 0
    assert {"country", "iso", "year", "value"} <= set(records[0].keys())
    assert any(r["iso"] == "ES" for r in records)


@respx.mock
def test_eu_unemployment_view_returns_records(
    client: TestClient, eurostat_unemployment: dict[str, Any]
) -> None:
    respx.get(f"{EUROSTAT_BASE}/une_rt_a").mock(
        return_value=httpx.Response(200, json=eurostat_unemployment)
    )
    response = client.get("/api/datasets/eu/labor/views/unemployment-rate?nult=6")
    assert response.status_code == 200
    payload = response.json()
    assert payload["view"]["category_col"] == "country"
    records = payload["records"]
    assert len(records) > 0
    assert {"country", "year", "value"} <= set(records[0].keys())


def test_countries_default_locale_is_spanish(client: TestClient) -> None:
    es = next(c for c in client.get("/api/countries").json() if c["code"] == "es")
    assert es["name"] == "España"
    crime = next(d for d in es["datasets"] if d["key"] == "crime")
    assert crime["label"] == "Criminalidad"


def test_countries_localized_to_english(client: TestClient) -> None:
    es = next(c for c in client.get("/api/countries?lang=en").json() if c["code"] == "es")
    assert es["name"] == "Spain"
    crime = next(d for d in es["datasets"] if d["key"] == "crime")
    assert crime["label"] == "Crime"


def test_views_localized_to_english(client: TestClient) -> None:
    views = client.get("/api/datasets/es/crime/views?lang=en").json()
    by_type = next(v for v in views if v["key"] == "offenses-by-type")
    assert by_type["label"] == "Offences by type"
    assert by_type["category_label"] == "Offence type"


def test_unknown_lang_falls_back_to_spanish(client: TestClient) -> None:
    es = next(c for c in client.get("/api/countries?lang=fr").json() if c["code"] == "es")
    assert es["name"] == "España"


# --- API v1 (contrato estable) + deprecación de /api ---


def test_v1_health(client: TestClient) -> None:
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_v1_countries(client: TestClient) -> None:
    response = client.get("/api/v1/countries")
    assert response.status_code == 200
    codes = {c["code"] for c in response.json()}
    assert {"es", "eu"} <= codes


def test_v1_views_and_404s(client: TestClient) -> None:
    assert client.get("/api/v1/datasets/es/crime/views").status_code == 200
    assert client.get("/api/v1/datasets/xx/crime/views").status_code == 404


@respx.mock
def test_v1_get_view_returns_records(
    client: TestClient, ine_crime_25997: list[dict[str, Any]]
) -> None:
    respx.get(f"{BASE}/DATOS_TABLA/25997").mock(
        return_value=httpx.Response(200, json=ine_crime_25997)
    )
    response = client.get("/api/v1/datasets/es/crime/views/offenses-by-type?nult=3")
    assert response.status_code == 200
    assert response.json()["view"]["key"] == "offenses-by-type"


def test_legacy_alias_still_works(client: TestClient) -> None:
    # /api (sin v1) sigue respondiendo como alias deprecado.
    assert client.get("/api/countries").status_code == 200


def test_openapi_marks_legacy_deprecated_not_v1() -> None:
    paths = app.openapi()["paths"]
    assert paths["/api/countries"]["get"]["deprecated"] is True
    assert paths["/api/v1/countries"]["get"].get("deprecated", False) is False


def test_serves_from_snapshot_without_hitting_source(client: TestClient) -> None:
    # Persistimos un snapshot y comprobamos que la API lo sirve sin red (sin respx mock).
    df = pd.DataFrame(
        {
            "scope": ["Total", "Total"],
            "metric": ["Dato base", "Dato base"],
            "offense_type": ["Robo", "Hurto"],
            "year": [2024, 2024],
            "value": [10.0, 20.0],
        }
    )
    storage.write_view("es", "crime", "offenses-by-type", df, source="INE")

    response = client.get("/api/v1/datasets/es/crime/views/offenses-by-type?nult=5")
    assert response.status_code == 200
    payload = response.json()
    records = payload["records"]
    assert {r["offense_type"] for r in records} == {"Robo", "Hurto"}
    # servido desde snapshot → expone la procedencia
    assert payload["fetched_at"] is not None
