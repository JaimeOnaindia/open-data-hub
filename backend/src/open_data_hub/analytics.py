"""Capa analítica: relacionar fuentes con DuckDB sobre los parquet del almacén.

DuckDB da SQL con joins sin servidor, leyendo directamente los snapshots. Es el primer
paso hacia "relacionar datos": unir indicadores entre países por la dimensión canónica
ISO. El día que se justifique, un star schema sale de aquí con un `CREATE TABLE AS SELECT`.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from open_data_hub.core import storage


def relate_eu_indicators(*, base: Path | None = None) -> pd.DataFrame:
    """Une paro e IPCA (Eurostat) por país (ISO) y año. Columnas: iso, country, year,
    unemployment, hicp. Vacío si aún no se han ingestado ambas vistas."""
    unemployment = storage.view_path("eu", "labor", "unemployment-rate", base=base)
    prices = storage.view_path("eu", "prices", "hicp-annual", base=base)
    if not unemployment.exists() or not prices.exists():
        return pd.DataFrame(columns=["iso", "country", "year", "unemployment", "hicp"])

    con = duckdb.connect(":memory:")
    try:
        result: pd.DataFrame = con.execute(
            """
            SELECT u.iso, u.country, u.year,
                   u.value AS unemployment, p.value AS hicp
            FROM read_parquet(?) AS u
            JOIN read_parquet(?) AS p USING (iso, year)
            WHERE u.iso IS NOT NULL
            ORDER BY u.iso, u.year
            """,
            [str(unemployment), str(prices)],
        ).df()
    finally:
        con.close()
    return result
