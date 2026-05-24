"""🇪🇸 España — Instituto Nacional de Estadística (INE)."""

from __future__ import annotations

from open_data_hub.core.registry import CountryConfig, DatasetConfig
from open_data_hub.countries.es.sources.ine_datasets import ES_DATASET_VIEWS as VIEWS

COUNTRY = CountryConfig(
    code="es",
    name="España",
    flag="🇪🇸",
    datasets=[
        DatasetConfig(
            key="crime",
            label="Criminalidad",
            description=(
                "Estadística de Condenados (adultos). Delitos por tipo, sexo y nacionalidad."
            ),
            source_name="INE",
        ),
        DatasetConfig(
            key="prices",
            label="Precios",
            description="Índice de Precios de Consumo nacional por grupos ECOICOP.",
            source_name="INE",
        ),
        DatasetConfig(
            key="labor",
            label="Mercado laboral",
            description="Tasas de paro por territorio, sexo y grupo de edad.",
            source_name="INE",
        ),
        DatasetConfig(
            key="demography",
            label="Demografía",
            description="Indicadores demográficos básicos y fenómenos demográficos.",
            source_name="INE",
        ),
    ],
)

__all__ = ["COUNTRY", "VIEWS"]
