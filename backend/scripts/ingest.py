"""Ejecuta la ingesta de todos los datasets a parquet (`data/snapshots/`).

Hace peticiones en vivo a las fuentes oficiales. Uso: `make ingest`.
"""

from __future__ import annotations

import sys

from open_data_hub.ingest import ingest_all

if __name__ == "__main__":
    total = 0
    for country_code, dataset_key, view_key, rows in ingest_all():
        total += rows
        print(f"{country_code}/{dataset_key}/{view_key}: {rows} filas", file=sys.stderr)
    print(f"Total: {total} filas persistidas", file=sys.stderr)
