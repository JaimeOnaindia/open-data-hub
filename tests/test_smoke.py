"""Smoke tests: el paquete importa y la API arranca."""

from __future__ import annotations

from fastapi.testclient import TestClient

from open_data_hub.api import app
from open_data_hub.countries.catalog import COUNTRIES


def test_package_importable() -> None:
    assert "es" in COUNTRIES
    assert COUNTRIES["es"].name == "España"


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_countries_includes_spain() -> None:
    client = TestClient(app)
    response = client.get("/api/countries")
    assert response.status_code == 200
    countries = response.json()
    codes = [c["code"] for c in countries]
    assert "es" in codes
