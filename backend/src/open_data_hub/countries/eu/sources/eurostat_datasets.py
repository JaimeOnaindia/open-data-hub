from __future__ import annotations

import pandas as pd

from open_data_hub.core.datasets import CountryDatasetViews, DatasetViewConfig
from open_data_hub.core.i18n import L
from open_data_hub.countries.eu.sources.eurostat_client import EurostatClient

# (código del dataset Eurostat, filtros fijos que dejan variar geo y time)
EUROSTAT_QUERIES: dict[str, tuple[str, dict[str, str]]] = {
    "unemployment": ("une_rt_a", {"sex": "T", "age": "Y15-74", "unit": "PC_ACT"}),
    "hicp": ("prc_hicp_aind", {"coicop": "CP00", "unit": "RCH_A_AVG"}),
}


def _fetch(query_key: str, *, client: EurostatClient | None, nult: int) -> pd.DataFrame:
    code, base = EUROSTAT_QUERIES[query_key]
    own_client = client is None
    client = client or EurostatClient()
    try:
        params: dict[str, str | int] = {**base, "lastTimePeriod": nult}
        df = client.get_dataset_df(code, params=params)
    finally:
        if own_client:
            client.close()

    if df.empty:
        return df
    df = df.rename(columns={"geo": "country"})
    return df[["country", "year", "value"]]


def fetch_unemployment(*, client: EurostatClient | None = None, nult: int = 10) -> pd.DataFrame:
    """une_rt_a — Tasa de paro anual (ambos sexos, 15-74, % población activa) por país."""
    return _fetch("unemployment", client=client, nult=nult)


def fetch_hicp(*, client: EurostatClient | None = None, nult: int = 10) -> pd.DataFrame:
    """prc_hicp_aind — IPCA, variación anual media (CP00 todos los grupos) por país."""
    return _fetch("hicp", client=client, nult=nult)


EU_DATASET_VIEWS: CountryDatasetViews = {
    "labor": {
        "unemployment-rate": DatasetViewConfig(
            key="unemployment-rate",
            label=L("Tasa de paro por país", "Unemployment rate by country"),
            fetcher=fetch_unemployment,
            category_col="country",
            category_label=L("País", "Country"),
            filter_cols=(),
        ),
    },
    "prices": {
        "hicp-annual": DatasetViewConfig(
            key="hicp-annual",
            label=L("IPCA — variación anual por país", "HICP — annual change by country"),
            fetcher=fetch_hicp,
            category_col="country",
            category_label=L("País", "Country"),
            filter_cols=(),
        ),
    },
}
