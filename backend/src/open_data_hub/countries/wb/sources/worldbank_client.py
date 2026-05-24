from __future__ import annotations

from typing import Any

import httpx
import pandas as pd
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from open_data_hub.harmonize.geo import is_iso2_country


class WorldBankClient:
    """Cliente para la API de indicadores del Banco Mundial (formato JSON nativo).

    Endpoint: https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}
    La respuesta es `[meta, filas]`; `country.id` es ISO 3166-1 alpha-2 para países y
    códigos no-ISO (1W, EU, XC, Z4…) para agregados, que descartamos.
    """

    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self, *, timeout: float = 60.0, base_url: str | None = None) -> None:
        self._client = httpx.Client(
            base_url=base_url or self.BASE_URL,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> WorldBankClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        reraise=True,
    )
    def _get_page(
        self, indicator: str, *, countries: str, date_range: str | None, per_page: int, page: int
    ) -> list[Any]:
        params: dict[str, str | int] = {"format": "json", "per_page": per_page, "page": page}
        if date_range:
            params["date"] = date_range
        response = self._client.get(f"/country/{countries}/indicator/{indicator}", params=params)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError(f"Respuesta inesperada del Banco Mundial para {indicator}")
        return payload

    def get_indicator(
        self,
        indicator: str,
        *,
        countries: str = "all",
        date_range: str | None = None,
        per_page: int = 20000,
    ) -> list[dict[str, Any]]:
        """Devuelve las filas crudas del indicador, paginando si hace falta."""
        rows: list[dict[str, Any]] = []
        page = 1
        while True:
            meta, data = self._get_page(
                indicator,
                countries=countries,
                date_range=date_range,
                per_page=per_page,
                page=page,
            )
            if data:
                rows.extend(data)
            if page >= int(meta.get("pages", 1)):
                break
            page += 1
        return rows

    def get_indicator_df(
        self, indicator: str, *, countries: str = "all", date_range: str | None = None
    ) -> pd.DataFrame:
        """Aplana un indicador en un DataFrame tidy (country, iso, year, value), solo países."""
        out: list[dict[str, Any]] = []
        for row in self.get_indicator(indicator, countries=countries, date_range=date_range):
            country = row.get("country") or {}
            code = country.get("id")
            value = row.get("value")
            if value is None or not is_iso2_country(code):
                continue
            try:
                year = int(row["date"])
            except (KeyError, TypeError, ValueError):
                continue
            out.append(
                {
                    "country": country.get("value", code),
                    "iso": str(code).upper(),
                    "year": year,
                    "value": float(value),
                }
            )
        return pd.DataFrame(out)
