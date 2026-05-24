from __future__ import annotations

import re
from typing import Any

import httpx
import pandas as pd
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class INEClient:
    """Cliente para la API tempus3 del INE (formato JSON nativo, no JSON-stat).

    Endpoint: https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{table_id}
    Docs: https://www.ine.es/dyngs/DAB/index.htm?cid=1100
    """

    BASE_URL = "https://servicios.ine.es/wstempus/js/ES"

    def __init__(self, *, timeout: float = 30.0, base_url: str | None = None) -> None:
        self._client = httpx.Client(
            base_url=base_url or self.BASE_URL,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> INEClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        reraise=True,
    )
    def get_table(self, table_id: int, *, nult: int | None = None) -> list[dict[str, Any]]:
        """Devuelve la lista cruda de series de una tabla del INE.

        `nult` limita a las N últimas observaciones por serie (recomendado para reducir payload).
        """
        params: dict[str, str | int] = {}
        if nult is not None:
            params["nult"] = nult
        response = self._client.get(f"/DATOS_TABLA/{table_id}", params=params)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError(f"Respuesta inesperada del INE para tabla {table_id}: {type(payload)}")
        return payload

    def get_table_df(
        self,
        table_id: int,
        *,
        nult: int | None = 10,
        dim_names: list[str] | None = None,
    ) -> pd.DataFrame:
        """Aplana la tabla en un DataFrame tidy.

        Una fila por (serie, periodo). El campo `Nombre` del INE codifica las dimensiones
        separadas normalmente por ". " o por comas en algunas tablas tpx: se divide en
        columnas `dim_0`, `dim_1`, … o con los nombres dados en `dim_names`.
        """
        series = self.get_table(table_id, nult=nult)
        rows: list[dict[str, Any]] = []
        for serie in series:
            name = str(serie.get("Nombre", ""))
            parts = _split_series_name(name)
            cod = serie.get("COD")
            for obs in serie.get("Data", []):
                if obs.get("Secreto"):
                    continue
                value = obs.get("Valor")
                year = _year_from_observation(obs)
                if value is None or year is None:
                    continue
                row: dict[str, Any] = {"series_cod": cod, "series_name": name}
                for idx, part in enumerate(parts):
                    row[f"dim_{idx}"] = part
                row["year"] = int(year)
                row["period"] = str(obs.get("NombrePeriodo") or year)
                if obs.get("FK_Periodo") is not None:
                    row["period_code"] = int(obs["FK_Periodo"])
                row["value"] = float(value)
                rows.append(row)

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        if dim_names:
            rename = {
                f"dim_{i}": name
                for i, name in enumerate(dim_names)
                if f"dim_{i}" in df.columns
            }
            df = df.rename(columns=rename)

        return df


def _split_series_name(name: str) -> list[str]:
    separator = "." if "." in name else ","
    return [part.strip() for part in name.split(separator) if part.strip()]


def _year_from_observation(obs: dict[str, Any]) -> int | None:
    year = obs.get("Anyo")
    if year is not None:
        return int(year)

    period = obs.get("NombrePeriodo")
    if period is None:
        return None

    match = re.search(r"\d{4}", str(period))
    if match is None:
        return None
    return int(match.group(0))
