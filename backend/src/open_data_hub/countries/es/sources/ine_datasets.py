from __future__ import annotations

from typing import Any, cast

import pandas as pd

from open_data_hub.core.datasets import CountryDatasetViews, DatasetViewConfig
from open_data_hub.core.i18n import L
from open_data_hub.countries.es.sources.crime import (
    fetch_convicted_by_sex_nationality,
    fetch_offenses_by_nationality,
    fetch_offenses_by_sex,
    fetch_offenses_by_type,
    fetch_sexual_offenses,
)
from open_data_hub.countries.es.sources.ine_client import INEClient

INE_TABLES: dict[str, int] = {
    "consumer_prices": 50902,
    "unemployment_rates": 74999,
    "life_expectancy": 73559,
    "demographic_events": 73758,
}

SEX_VALUES = {"Ambos sexos", "Hombres", "Mujeres"}


def fetch_consumer_prices(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 50902 — IPC nacional por grupos ECOICOP."""
    return _fetch_ine_table(
        "consumer_prices",
        ["territory", "category", "metric"],
        client=client,
        nult=nult,
    )


def fetch_unemployment_rates(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 74999 — Tasas de paro por edad, sexo y comunidad autónoma."""
    df = _fetch_ine_table(
        "unemployment_rates",
        ["indicator", "dimension_1", "dimension_2", "age_group"],
        client=client,
        nult=nult,
    )
    if df.empty:
        return df

    records = cast(list[dict[str, Any]], df.to_dict(orient="records"))
    sexes: list[str] = []
    territories: list[str] = []
    for record in records:
        dimension_1 = str(record.get("dimension_1", ""))
        dimension_2 = str(record.get("dimension_2", ""))
        if dimension_1 in SEX_VALUES:
            sexes.append(dimension_1)
            territories.append(dimension_2)
        else:
            territories.append(dimension_1)
            sexes.append(dimension_2)

    return df.assign(sex=sexes, territory=territories)


def fetch_life_expectancy(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 73559 — Esperanza de vida al nacimiento por sexo."""
    return _fetch_ine_table(
        "life_expectancy",
        ["territory", "sex"],
        client=client,
        nult=nult,
    )


def fetch_demographic_events(
    *, client: INEClient | None = None, nult: int = 10
) -> pd.DataFrame:
    """Tabla 73758 — Nacimientos, defunciones, matrimonios y otros fenómenos."""
    return _fetch_ine_table(
        "demographic_events",
        ["operation", "event"],
        client=client,
        nult=nult,
    )


def _fetch_ine_table(
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
            INE_TABLES[table_key],
            nult=nult,
            dim_names=dim_names,
        )
    finally:
        if own_client:
            client.close()


ES_DATASET_VIEWS: CountryDatasetViews = {
    "crime": {
        "offenses-by-type": DatasetViewConfig(
            key="offenses-by-type",
            label=L("Delitos según tipo", "Offences by type"),
            fetcher=fetch_offenses_by_type,
            category_col="offense_type",
            category_label=L("Tipo de delito", "Offence type"),
            filter_cols=("metric",),
        ),
        "offenses-by-sex": DatasetViewConfig(
            key="offenses-by-sex",
            label=L("Delitos por tipo y sexo", "Offences by type and sex"),
            fetcher=fetch_offenses_by_sex,
            category_col="offense_type",
            category_label=L("Tipo de delito", "Offence type"),
            filter_cols=("metric", "sex"),
        ),
        "offenses-by-nationality": DatasetViewConfig(
            key="offenses-by-nationality",
            label=L("Delitos por tipo y nacionalidad", "Offences by type and nationality"),
            fetcher=fetch_offenses_by_nationality,
            category_col="offense_type",
            category_label=L("Tipo de delito", "Offence type"),
            filter_cols=("metric", "nationality"),
        ),
        "sexual-offenses": DatasetViewConfig(
            key="sexual-offenses",
            label=L("Delitos sexuales por tipo", "Sexual offences by type"),
            fetcher=fetch_sexual_offenses,
            category_col="offense_type",
            category_label=L("Tipo de delito sexual", "Sexual offence type"),
            filter_cols=("metric", "nationality"),
        ),
        "convicted-by-sex-nationality": DatasetViewConfig(
            key="convicted-by-sex-nationality",
            label=L("Condenados por sexo y nacionalidad", "Convicts by sex and nationality"),
            fetcher=fetch_convicted_by_sex_nationality,
            category_col="nationality",
            category_label=L("Nacionalidad", "Nationality"),
            filter_cols=("metric", "sex", "num_offenses"),
        ),
    },
    "prices": {
        "consumer-prices": DatasetViewConfig(
            key="consumer-prices",
            label=L("IPC nacional por grupos", "National CPI by group"),
            fetcher=fetch_consumer_prices,
            category_col="category",
            category_label=L("Grupo ECOICOP", "ECOICOP group"),
            filter_cols=("metric",),
        ),
    },
    "labor": {
        "unemployment-rates": DatasetViewConfig(
            key="unemployment-rates",
            label=L("Tasa de paro por territorio", "Unemployment rate by territory"),
            fetcher=fetch_unemployment_rates,
            category_col="territory",
            category_label=L("Territorio", "Territory"),
            filter_cols=("sex", "age_group"),
        ),
    },
    "demography": {
        "life-expectancy": DatasetViewConfig(
            key="life-expectancy",
            label=L("Esperanza de vida al nacimiento", "Life expectancy at birth"),
            fetcher=fetch_life_expectancy,
            category_col="sex",
            category_label=L("Sexo", "Sex"),
            filter_cols=(),
        ),
        "demographic-events": DatasetViewConfig(
            key="demographic-events",
            label=L("Fenómenos demográficos", "Vital events"),
            fetcher=fetch_demographic_events,
            category_col="event",
            category_label=L("Fenómeno", "Event"),
            filter_cols=("operation",),
        ),
    },
}
