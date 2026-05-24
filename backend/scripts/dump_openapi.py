"""Vuelca el esquema OpenAPI de la API a stdout.

Se usa para generar los tipos TypeScript del frontend (single source of truth:
modelos pydantic → OpenAPI → tipos TS). Ver `make openapi` / `make types`.
"""

from __future__ import annotations

import json

from open_data_hub.api import app

if __name__ == "__main__":
    print(json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True))
