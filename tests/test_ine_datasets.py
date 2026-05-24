"""Tests específicos de los datasets ES (prices, labor, demography)."""

from __future__ import annotations

import httpx
import pytest
import respx

from open_data_hub.core.i18n import resolve
from open_data_hub.countries.catalog import COUNTRIES, get_country
from open_data_hub.countries.es.sources.ine_datasets import (
    INE_TABLES,
    fetch_consumer_prices,
    fetch_demographic_events,
    fetch_life_expectancy,
    fetch_unemployment_rates,
)

BASE = "https://servicios.ine.es/wstempus/js/ES"


def test_get_country_known_returns_config() -> None:
    assert get_country("es").code == "es"
    assert get_country("ES").code == "es"


def test_get_country_unknown_raises() -> None:
    with pytest.raises(KeyError, match="País 'xx'"):
        get_country("xx")


def test_country_dataset_lookup() -> None:
    es = COUNTRIES["es"]
    crime = es.dataset("crime")
    assert resolve(crime.label, "es") == "Criminalidad"
    assert resolve(crime.label, "en") == "Crime"
    with pytest.raises(KeyError, match="Dataset 'nope'"):
        es.dataset("nope")


@respx.mock
def test_fetch_consumer_prices_parses_dimensions() -> None:
    payload = [
        {
            "COD": "P1",
            "Nombre": "Nacional. Grupo general. Índice. ",
            "Data": [
                {"Anyo": 2024, "Valor": 110.5, "Secreto": False, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/{INE_TABLES['consumer_prices']}").mock(
        return_value=httpx.Response(200, json=payload)
    )
    df = fetch_consumer_prices(nult=1)
    assert df["territory"].iloc[0] == "Nacional"
    assert df["category"].iloc[0] == "Grupo general"
    assert df["metric"].iloc[0] == "Índice"


@respx.mock
def test_fetch_unemployment_rates_handles_sex_first_dimension() -> None:
    payload = [
        {
            "COD": "U1",
            "Nombre": "Tasa de paro. Hombres. Andalucía. De 20 a 24 años",
            "Data": [
                {"Anyo": 2024, "Valor": 19.4, "Secreto": False, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/{INE_TABLES['unemployment_rates']}").mock(
        return_value=httpx.Response(200, json=payload)
    )
    df = fetch_unemployment_rates(nult=1)
    assert df["sex"].iloc[0] == "Hombres"
    assert df["territory"].iloc[0] == "Andalucía"


@respx.mock
def test_fetch_unemployment_rates_handles_sex_second_dimension() -> None:
    payload = [
        {
            "COD": "U2",
            "Nombre": "Tasa de paro. Cataluña. Mujeres. De 25 y más años",
            "Data": [
                {"Anyo": 2024, "Valor": 12.1, "Secreto": False, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/{INE_TABLES['unemployment_rates']}").mock(
        return_value=httpx.Response(200, json=payload)
    )
    df = fetch_unemployment_rates(nult=1)
    assert df["sex"].iloc[0] == "Mujeres"
    assert df["territory"].iloc[0] == "Cataluña"


@respx.mock
def test_fetch_unemployment_rates_empty_short_circuits() -> None:
    respx.get(f"{BASE}/DATOS_TABLA/{INE_TABLES['unemployment_rates']}").mock(
        return_value=httpx.Response(200, json=[])
    )
    df = fetch_unemployment_rates(nult=1)
    assert df.empty


@respx.mock
def test_fetch_life_expectancy() -> None:
    payload = [
        {
            "COD": "L1",
            "Nombre": "España. Ambos sexos. ",
            "Data": [
                {"Anyo": 2024, "Valor": 83.4, "Secreto": False, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/{INE_TABLES['life_expectancy']}").mock(
        return_value=httpx.Response(200, json=payload)
    )
    df = fetch_life_expectancy(nult=1)
    assert df["territory"].iloc[0] == "España"
    assert df["sex"].iloc[0] == "Ambos sexos"


@respx.mock
def test_fetch_demographic_events() -> None:
    payload = [
        {
            "COD": "D1",
            "Nombre": "Cifras nacionales. Nacimientos. ",
            "Data": [
                {"Anyo": 2024, "Valor": 320000.0, "Secreto": False, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/{INE_TABLES['demographic_events']}").mock(
        return_value=httpx.Response(200, json=payload)
    )
    df = fetch_demographic_events(nult=1)
    assert df["operation"].iloc[0] == "Cifras nacionales"
    assert df["event"].iloc[0] == "Nacimientos"
