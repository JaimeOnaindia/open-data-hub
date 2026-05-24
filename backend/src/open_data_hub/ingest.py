"""Ingesta: recorre el catálogo, llama a cada fetcher y persiste el resultado.

Reutiliza los mismos `fetch_*` que servían en vivo; aquí pasan a alimentar el almacén.
Hace peticiones reales a las fuentes oficiales, así que se ejecuta manualmente o por
cron (`make ingest`), nunca en los tests/CI.
"""

from __future__ import annotations

from pathlib import Path

from open_data_hub.core import storage
from open_data_hub.countries.catalog import COUNTRIES, DATASET_VIEWS_BY_COUNTRY

# Ventana amplia al ingerir: las fuentes devuelven lo disponible hasta este límite.
INGEST_NULT = 50


def _source_for(country_code: str, dataset_key: str) -> str:
    country = COUNTRIES.get(country_code)
    if country is None:
        return ""
    try:
        return country.dataset(dataset_key).source_name
    except KeyError:
        return ""


def ingest_view(
    country_code: str,
    dataset_key: str,
    view_key: str,
    *,
    nult: int = INGEST_NULT,
    base: Path | None = None,
) -> int:
    """Ingesta una vista y devuelve el nº de filas persistidas."""
    config = DATASET_VIEWS_BY_COUNTRY[country_code][dataset_key][view_key]
    df = config.fetcher(nult=nult)
    storage.write_view(
        country_code,
        dataset_key,
        view_key,
        df,
        source=_source_for(country_code, dataset_key),
        base=base,
    )
    return len(df)


def ingest_all(
    *, nult: int = INGEST_NULT, base: Path | None = None
) -> list[tuple[str, str, str, int]]:
    """Ingesta todas las vistas registradas. Devuelve (cc, dataset, view, filas)."""
    results: list[tuple[str, str, str, int]] = []
    for country_code, datasets in DATASET_VIEWS_BY_COUNTRY.items():
        for dataset_key, views in datasets.items():
            for view_key in views:
                rows = ingest_view(country_code, dataset_key, view_key, nult=nult, base=base)
                results.append((country_code, dataset_key, view_key, rows))
    return results
