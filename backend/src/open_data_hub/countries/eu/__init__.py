"""🇪🇺 Unión Europea — Eurostat (fuente multilateral, datos comparados entre países)."""

from __future__ import annotations

from open_data_hub.core.registry import CountryConfig, DatasetConfig
from open_data_hub.countries.eu.sources.eurostat_datasets import EU_DATASET_VIEWS as VIEWS

COUNTRY = CountryConfig(
    code="eu",
    name="Unión Europea (Eurostat)",
    flag="🇪🇺",
    datasets=[
        DatasetConfig(
            key="labor",
            label="Mercado laboral",
            description="Tasa de paro anual comparada entre países europeos.",
            source_name="Eurostat",
        ),
        DatasetConfig(
            key="prices",
            label="Precios",
            description="IPCA — variación anual media de precios por país europeo.",
            source_name="Eurostat",
        ),
    ],
)

__all__ = ["COUNTRY", "VIEWS"]
