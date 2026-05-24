from __future__ import annotations

import pandas as pd

from open_data_hub.countries.es.sources.ine_client import INEClient

# Tablas INE — Estadística de Condenados (adultos).
# Catálogo: https://www.ine.es/dynt3/inebase/es/index.htm?padre=2399
CRIME_TABLES: dict[str, int] = {
    "offenses_by_type": 25997,
    "offenses_by_sex": 25998,
    "offenses_by_nationality": 26014,
    "convicted_by_sex_nationality": 25698,
    "sexual_offenses": 28716,
}


def _fetch(
    table_key: str,
    dim_names: list[str],
    *,
    client: INEClient | None,
    nult: int,
) -> pd.DataFrame:
    own_client = client is None
    client = client or INEClient()
    try:
        return client.get_table_df(
            CRIME_TABLES[table_key],
            nult=nult,
            dim_names=dim_names,
        )
    finally:
        if own_client:
            client.close()


def fetch_offenses_by_type(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 25997 — Delitos según tipo."""
    return _fetch(
        "offenses_by_type",
        ["scope", "metric", "offense_type"],
        client=client,
        nult=nult,
    )


def fetch_offenses_by_sex(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 25998 — Delitos cruzando tipo y sexo del condenado."""
    return _fetch(
        "offenses_by_sex",
        ["scope", "metric", "offense_type", "sex"],
        client=client,
        nult=nult,
    )


def fetch_offenses_by_nationality(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 26014 — Delitos cruzando tipo y nacionalidad del condenado."""
    return _fetch(
        "offenses_by_nationality",
        ["scope", "metric", "offense_type", "nationality"],
        client=client,
        nult=nult,
    )


def fetch_sexual_offenses(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 28716 — Delitos sexuales (por tipo de delito y nacionalidad)."""
    return _fetch(
        "sexual_offenses",
        ["scope", "metric", "offense_type", "nationality", "category"],
        client=client,
        nult=nult,
    )


def fetch_convicted_by_sex_nationality(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 25698 — Condenados cruzando sexo, nº de delitos y nacionalidad."""
    return _fetch(
        "convicted_by_sex_nationality",
        ["scope", "sex", "metric", "num_offenses", "nationality"],
        client=client,
        nult=nult,
    )
