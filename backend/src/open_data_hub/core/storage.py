"""Persistencia de vistas en parquet.

Cada vista se guarda como `<base>/<cc>/<dataset>/<view>.parquet` con un sidecar
`<view>.meta.json` de procedencia (`fetched_at`, fuente, nº de filas). La API lee de
aquí (con fallback en vivo si no hay snapshot); la ingesta escribe aquí.

El directorio base se resuelve en tiempo de llamada desde `OPEN_DATA_HUB_DATA_DIR`
(por defecto `data/snapshots`), para que sea configurable por entorno.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pandas as pd

DEFAULT_DIR = Path("data/snapshots")


def snapshot_dir() -> Path:
    return Path(os.environ.get("OPEN_DATA_HUB_DATA_DIR", str(DEFAULT_DIR)))


def view_path(
    country_code: str, dataset_key: str, view_key: str, *, base: Path | None = None
) -> Path:
    root = base if base is not None else snapshot_dir()
    return root / country_code / dataset_key / f"{view_key}.parquet"


def _meta_path(path: Path) -> Path:
    return path.parent / f"{path.stem}.meta.json"


def write_view(
    country_code: str,
    dataset_key: str,
    view_key: str,
    df: pd.DataFrame,
    *,
    source: str = "",
    base: Path | None = None,
) -> Path:
    """Escribe la vista en parquet + un sidecar de procedencia. Devuelve la ruta parquet."""
    path = view_path(country_code, dataset_key, view_key, base=base)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

    meta = {
        "country_code": country_code,
        "dataset_key": dataset_key,
        "view_key": view_key,
        "source": source,
        "rows": int(len(df)),
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    _meta_path(path).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_view(
    country_code: str, dataset_key: str, view_key: str, *, base: Path | None = None
) -> pd.DataFrame | None:
    """Lee la vista persistida, o `None` si aún no se ha ingestado."""
    path = view_path(country_code, dataset_key, view_key, base=base)
    if not path.exists():
        return None
    return pd.read_parquet(path)


def read_meta(
    country_code: str, dataset_key: str, view_key: str, *, base: Path | None = None
) -> dict[str, Any] | None:
    """Lee la procedencia de la vista, o `None` si no existe."""
    path = _meta_path(view_path(country_code, dataset_key, view_key, base=base))
    if not path.exists():
        return None
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
