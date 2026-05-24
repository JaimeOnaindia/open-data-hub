"""Tests del cliente tempus3 del INE.

Mockeamos la API con respx + fixtures reales capturados en tests/fixtures/ine/.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from open_data_hub.countries.es.sources.ine_client import INEClient

BASE = "https://servicios.ine.es/wstempus/js/ES"


@respx.mock
def test_get_table_returns_raw_list(ine_crime_25997: list[dict[str, Any]]) -> None:
    respx.get(f"{BASE}/DATOS_TABLA/25997").mock(
        return_value=httpx.Response(200, json=ine_crime_25997)
    )
    with INEClient() as client:
        payload = client.get_table(25997, nult=3)

    assert isinstance(payload, list)
    assert len(payload) == len(ine_crime_25997)
    assert {"COD", "Nombre", "Data"} <= set(payload[0].keys())


@respx.mock
def test_get_table_df_parses_dimensions_and_value(
    ine_crime_25997: list[dict[str, Any]],
) -> None:
    respx.get(f"{BASE}/DATOS_TABLA/25997").mock(
        return_value=httpx.Response(200, json=ine_crime_25997)
    )
    with INEClient() as client:
        df = client.get_table_df(
            25997,
            nult=3,
            dim_names=["scope", "metric", "offense_type"],
        )

    assert not df.empty
    assert {"scope", "metric", "offense_type", "year", "value", "series_cod"} <= set(df.columns)
    assert df["scope"].iloc[0] == "Total Nacional"
    assert df["metric"].iloc[0] == "Dato base"
    assert df["value"].dtype.kind == "f"
    assert df["year"].dtype.kind == "i"
    assert df["year"].min() >= 2000
    assert df["year"].max() <= 2030


@respx.mock
def test_get_table_df_filters_secret_observations() -> None:
    payload = [
        {
            "COD": "X1",
            "Nombre": "Total. Dato base. Robo. ",
            "Data": [
                {"Anyo": 2024, "Valor": 100.0, "Secreto": False, "FK_Periodo": 28},
                {"Anyo": 2023, "Valor": 50.0, "Secreto": True, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/999").mock(
        return_value=httpx.Response(200, json=payload)
    )
    with INEClient() as client:
        df = client.get_table_df(999, nult=2, dim_names=["scope", "metric", "offense_type"])

    assert len(df) == 1
    assert df["year"].iloc[0] == 2024


@respx.mock
def test_get_table_df_falls_back_to_nombre_periodo_for_year() -> None:
    payload = [
        {
            "COD": "X1",
            "Nombre": "Total. Dato. Cat. ",
            "Data": [
                {"NombrePeriodo": "2024", "Valor": 42.0, "Secreto": False},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/888").mock(
        return_value=httpx.Response(200, json=payload)
    )
    with INEClient() as client:
        df = client.get_table_df(888, nult=1, dim_names=["scope", "metric", "category"])

    assert df["year"].iloc[0] == 2024


@respx.mock
def test_get_table_df_supports_comma_separator() -> None:
    payload = [
        {
            "COD": "C1",
            "Nombre": "Madrid, Hombres, Total",
            "Data": [
                {"Anyo": 2024, "Valor": 5.5, "Secreto": False, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/777").mock(
        return_value=httpx.Response(200, json=payload)
    )
    with INEClient() as client:
        df = client.get_table_df(
            777,
            nult=1,
            dim_names=["territory", "sex", "metric"],
        )

    assert df["territory"].iloc[0] == "Madrid"
    assert df["sex"].iloc[0] == "Hombres"
    assert df["metric"].iloc[0] == "Total"


@respx.mock
def test_get_table_df_skips_missing_value_or_year() -> None:
    payload = [
        {
            "COD": "X1",
            "Nombre": "Total. Dato. Cat. ",
            "Data": [
                {"Anyo": 2024, "Valor": None, "Secreto": False},
                {"Anyo": None, "Valor": 10.0, "Secreto": False},
                {"Anyo": 2023, "Valor": 9.0, "Secreto": False, "FK_Periodo": 28},
            ],
        }
    ]
    respx.get(f"{BASE}/DATOS_TABLA/555").mock(
        return_value=httpx.Response(200, json=payload)
    )
    with INEClient() as client:
        df = client.get_table_df(555, nult=3, dim_names=["scope", "metric", "category"])

    assert len(df) == 1
    assert df["year"].iloc[0] == 2023


@respx.mock
def test_get_table_raises_on_non_list_payload() -> None:
    respx.get(f"{BASE}/DATOS_TABLA/666").mock(
        return_value=httpx.Response(200, json={"error": "unexpected"})
    )
    with INEClient() as client, pytest.raises(ValueError, match="Respuesta inesperada"):
        client.get_table(666, nult=1)


@respx.mock
def test_get_table_retries_on_http_error() -> None:
    route = respx.get(f"{BASE}/DATOS_TABLA/444").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(503),
            httpx.Response(200, json=[]),
        ]
    )
    with INEClient() as client:
        payload = client.get_table(444, nult=1)

    assert payload == []
    assert route.call_count == 3


def test_get_table_df_empty_returns_empty_frame() -> None:
    with respx.mock(base_url=BASE) as mock:
        mock.get("/DATOS_TABLA/333").mock(return_value=httpx.Response(200, json=[]))
        with INEClient() as client:
            df = client.get_table_df(333, nult=1, dim_names=["a", "b"])

    assert df.empty
