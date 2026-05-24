"""Demostración: relaciona paro vs IPCA por país (ISO) leyendo los parquet con DuckDB.

Requiere haber ejecutado `make ingest` antes. Uso: `make relate`.
"""

from __future__ import annotations

import sys

from open_data_hub.analytics import relate_eu_indicators

if __name__ == "__main__":
    df = relate_eu_indicators()
    if df.empty:
        print("Sin datos. Ejecuta 'make ingest' primero.", file=sys.stderr)
        sys.exit(0)
    print(df.to_string(index=False))
