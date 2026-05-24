"""🇪🇸 España — Instituto Nacional de Estadística (INE)."""

from __future__ import annotations

from open_data_hub.core.i18n import L
from open_data_hub.core.registry import CountryConfig, DatasetConfig
from open_data_hub.countries.es.sources.ine_datasets import ES_DATASET_VIEWS as VIEWS

COUNTRY = CountryConfig(
    code="es",
    name=L("España", "Spain"),
    flag="🇪🇸",
    datasets=[
        DatasetConfig(
            key="crime",
            label=L("Criminalidad", "Crime"),
            description=L(
                "Estadística de Condenados (adultos). Delitos por tipo, sexo y nacionalidad.",
                "Convictions statistics (adults). Offences by type, sex and nationality.",
            ),
            source_name="INE",
        ),
        DatasetConfig(
            key="prices",
            label=L("Precios", "Prices"),
            description=L(
                "Índice de Precios de Consumo nacional por grupos ECOICOP.",
                "National Consumer Price Index by ECOICOP groups.",
            ),
            source_name="INE",
        ),
        DatasetConfig(
            key="labor",
            label=L("Mercado laboral", "Labour market"),
            description=L(
                "Tasas de paro por territorio, sexo y grupo de edad.",
                "Unemployment rates by territory, sex and age group.",
            ),
            source_name="INE",
        ),
        DatasetConfig(
            key="demography",
            label=L("Demografía", "Demographics"),
            description=L(
                "Indicadores demográficos básicos y fenómenos demográficos.",
                "Basic demographic indicators and vital events.",
            ),
            source_name="INE",
        ),
    ],
)

__all__ = ["COUNTRY", "VIEWS"]
