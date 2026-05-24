from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Any

import httpx
import pandas as pd
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class EurostatClient:
    """Cliente para la API de difusión de Eurostat (formato JSON-stat 2.0).

    Endpoint: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}
    Docs: https://wikis.ec.europa.eu/display/EUROSTATHELP/API+-+Getting+started
    """

    BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

    def __init__(self, *, timeout: float = 30.0, base_url: str | None = None) -> None:
        self._client = httpx.Client(
            base_url=base_url or self.BASE_URL,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> EurostatClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        reraise=True,
    )
    def get_dataset(self, code: str, *, params: dict[str, str | int]) -> dict[str, Any]:
        """Devuelve el documento JSON-stat crudo de un dataset de Eurostat."""
        merged: dict[str, str | int] = {**params, "format": "JSON", "lang": "EN"}
        response = self._client.get(f"/{code}", params=merged)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or "value" not in payload:
            raise ValueError(f"Respuesta JSON-stat inesperada de Eurostat para {code}")
        return payload

    def get_dataset_df(self, code: str, *, params: dict[str, str | int]) -> pd.DataFrame:
        """Aplana un dataset de Eurostat en un DataFrame tidy.

        Una fila por celda no nula del hipercubo. Cada dimensión se convierte en una
        columna con su etiqueta humana; `time` se descompone en `period` y `year`.
        """
        return parse_jsonstat(self.get_dataset(code, params=params))


def parse_jsonstat(payload: dict[str, Any]) -> pd.DataFrame:
    """Convierte un documento JSON-stat 2.0 en un DataFrame tidy."""
    ids: list[str] = list(payload.get("id", []))
    sizes: list[int] = list(payload.get("size", []))
    dimensions: dict[str, Any] = payload.get("dimension", {})
    values: Any = payload.get("value", {})

    if not ids or not sizes:
        return pd.DataFrame()

    dim_codes: list[list[str]] = []
    dim_labels: list[dict[str, str]] = []
    for name in ids:
        category = dimensions.get(name, {}).get("category", {})
        index = category.get("index", {})
        if isinstance(index, dict):
            ordered = [code for code, _ in sorted(index.items(), key=lambda kv: kv[1])]
        else:
            ordered = list(index)
        dim_codes.append(ordered)
        dim_labels.append(category.get("label", {}))

    strides = _row_major_strides(sizes)

    rows: list[dict[str, Any]] = []
    for flat, value in _iter_values(values):
        if value is None:
            continue
        row: dict[str, Any] = {}
        year: int | None = None
        for d, name in enumerate(ids):
            pos = (flat // strides[d]) % sizes[d]
            code = dim_codes[d][pos]
            if name == "time":
                row["period"] = code
                year = _year_from_period(code)
            else:
                row[name] = dim_labels[d].get(code, code)
        if year is None:
            continue
        row["year"] = year
        row["value"] = float(value)
        rows.append(row)

    return pd.DataFrame(rows)


def _row_major_strides(sizes: list[int]) -> list[int]:
    strides = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    return strides


def _iter_values(values: Any) -> Iterable[tuple[int, Any]]:
    if isinstance(values, dict):
        return ((int(k), v) for k, v in values.items())
    return _enumerate_list(values)


def _enumerate_list(values: list[Any]) -> Iterator[tuple[int, Any]]:
    yield from enumerate(values)


def _year_from_period(period: str) -> int | None:
    match = re.search(r"\d{4}", period)
    return int(match.group(0)) if match else None
