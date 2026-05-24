"""🇪🇺 Unión Europea — Eurostat (fuente multilateral, datos comparados entre países)."""

from __future__ import annotations

from open_data_hub.core.i18n import L
from open_data_hub.core.registry import CountryConfig, DatasetConfig
from open_data_hub.countries.eu.sources.eurostat_datasets import EU_DATASET_VIEWS as VIEWS

COUNTRY = CountryConfig(
    code="eu",
    name=L("Unión Europea (Eurostat)", "European Union (Eurostat)"),
    flag="🇪🇺",
    datasets=[
        DatasetConfig(
            key="labor",
            label=L("Mercado laboral", "Labour market"),
            description=L(
                "Tasa de paro anual comparada entre países europeos.",
                "Annual unemployment rate compared across European countries.",
            ),
            source_name="Eurostat",
        ),
        DatasetConfig(
            key="prices",
            label=L("Precios", "Prices"),
            description=L(
                "IPCA — variación anual media de precios por país europeo.",
                "HICP — annual average price change by European country.",
            ),
            source_name="Eurostat",
        ),
    ],
)

__all__ = ["COUNTRY", "VIEWS"]
