"""Catálogo central de proveedores.

Para añadir un país o fuente multilateral:
  1. Crea `countries/<cc>/` exponiendo `COUNTRY` (CountryConfig) y `VIEWS` (CountryDatasetViews).
  2. Impórtalo aquí y añádelo a `_PROVIDERS`.

Nada más: la API y el frontend lo recogen automáticamente desde estos diccionarios.
"""

from __future__ import annotations

from open_data_hub.core.datasets import CountryDatasetViews
from open_data_hub.core.registry import CountryConfig
from open_data_hub.countries.es import COUNTRY as ES_COUNTRY
from open_data_hub.countries.es import VIEWS as ES_VIEWS
from open_data_hub.countries.eu import COUNTRY as EU_COUNTRY
from open_data_hub.countries.eu import VIEWS as EU_VIEWS
from open_data_hub.countries.wb import COUNTRY as WB_COUNTRY
from open_data_hub.countries.wb import VIEWS as WB_VIEWS

_PROVIDERS: list[tuple[CountryConfig, CountryDatasetViews]] = [
    (ES_COUNTRY, ES_VIEWS),
    (EU_COUNTRY, EU_VIEWS),
    (WB_COUNTRY, WB_VIEWS),
]

COUNTRIES: dict[str, CountryConfig] = {country.code: country for country, _ in _PROVIDERS}

DATASET_VIEWS_BY_COUNTRY: dict[str, CountryDatasetViews] = {
    country.code: views for country, views in _PROVIDERS
}


def get_country(code: str) -> CountryConfig:
    try:
        return COUNTRIES[code.lower()]
    except KeyError as exc:
        raise KeyError(f"País '{code}' no registrado") from exc
