"""Demostración: relaciona paro vs IPCA por país (ISO) leyendo los parquet con DuckDB.

Requiere haber ejecutado `make ingest` antes. Uso: `make relate`.
"""

from __future__ import annotations

import sys

from open_data_hub.analytics import relate_eu_indicators, relate_unemployment_sources

if __name__ == "__main__":
    eu = relate_eu_indicators()
    if eu.empty:
        print("Sin datos. Ejecuta 'make ingest' primero.", file=sys.stderr)
        sys.exit(0)
    print("== Eurostat: paro vs IPCA por país/año ==")
    print(eu.to_string(index=False))

    cross = relate_unemployment_sources()
    if not cross.empty:
        print("\n== Paro: Eurostat vs Banco Mundial (misma métrica, dos fuentes) ==")
        print(cross.to_string(index=False))
