from __future__ import annotations

import datetime

import pandas as pd

from open_data_hub.core.datasets import CountryDatasetViews, DatasetViewConfig
from open_data_hub.core.i18n import L
from open_data_hub.countries.wb.sources.worldbank_client import WorldBankClient

WB_INDICATORS: dict[str, str] = {
    "unemployment": "SL.UEM.TOTL.ZS",  # paro, % población activa
    "inflation": "FP.CPI.TOTL.ZG",  # inflación IPC, % anual
    "gdp-per-capita": "NY.GDP.PCAP.CD",  # PIB per cápita, US$ corrientes
}


def _fetch(indicator_key: str, *, client: WorldBankClient | None, nult: int) -> pd.DataFrame:
    own_client = client is None
    client = client or WorldBankClient()
    try:
        end = datetime.date.today().year
        date_range = f"{end - nult}:{end}"
        return client.get_indicator_df(WB_INDICATORS[indicator_key], date_range=date_range)
    finally:
        if own_client:
            client.close()


def fetch_unemployment(*, client: WorldBankClient | None = None, nult: int = 10) -> pd.DataFrame:
    """SL.UEM.TOTL.ZS — Tasa de paro (% población activa) por país."""
    return _fetch("unemployment", client=client, nult=nult)


def fetch_inflation(*, client: WorldBankClient | None = None, nult: int = 10) -> pd.DataFrame:
    """FP.CPI.TOTL.ZG — Inflación (IPC, variación anual %) por país."""
    return _fetch("inflation", client=client, nult=nult)


def fetch_gdp_per_capita(*, client: WorldBankClient | None = None, nult: int = 10) -> pd.DataFrame:
    """NY.GDP.PCAP.CD — PIB per cápita (US$ corrientes) por país."""
    return _fetch("gdp-per-capita", client=client, nult=nult)


WB_DATASET_VIEWS: CountryDatasetViews = {
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
        "inflation": DatasetViewConfig(
            key="inflation",
            label=L("Inflación anual por país", "Annual inflation by country"),
            fetcher=fetch_inflation,
            category_col="country",
            category_label=L("País", "Country"),
            filter_cols=(),
        ),
    },
    "economy": {
        "gdp-per-capita": DatasetViewConfig(
            key="gdp-per-capita",
            label=L("PIB per cápita por país", "GDP per capita by country"),
            fetcher=fetch_gdp_per_capita,
            category_col="country",
            category_label=L("País", "Country"),
            filter_cols=(),
        ),
    },
}
