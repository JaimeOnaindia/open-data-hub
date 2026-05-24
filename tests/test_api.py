"""Tests de la API FastAPI con TestClient + respx para mockear el INE."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from open_data_hub.api import _load_dataset_view, app

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
