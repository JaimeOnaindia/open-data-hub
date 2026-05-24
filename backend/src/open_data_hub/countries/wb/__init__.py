"""🌍 Banco Mundial — World Development Indicators (fuente multilateral, todos los países)."""

from __future__ import annotations

from open_data_hub.core.i18n import L
from open_data_hub.core.registry import CountryConfig, DatasetConfig
from open_data_hub.countries.wb.sources.worldbank_datasets import WB_DATASET_VIEWS as VIEWS

COUNTRY = CountryConfig(
    code="wb",
    name=L("Banco Mundial", "World Bank"),
    flag="🌍",
    datasets=[
        DatasetConfig(
            key="labor",
            label=L("Mercado laboral", "Labour market"),
            description=L(
                "Tasa de paro por país (estimación modelada OIT).",
                "Unemployment rate by country (modelled ILO estimate).",
            ),
            source_name="World Bank",
        ),
        DatasetConfig(
            key="prices",
            label=L("Precios", "Prices"),
            description=L(
                "Inflación anual de precios al consumo por país.",
                "Annual consumer price inflation by country.",
            ),
            source_name="World Bank",
        ),
        DatasetConfig(
            key="economy",
            label=L("Economía", "Economy"),
            description=L(
                "PIB per cápita (US$ corrientes) por país.",
                "GDP per capita (current US$) by country.",
            ),
            source_name="World Bank",
        ),
    ],
)

__all__ = ["COUNTRY", "VIEWS"]
