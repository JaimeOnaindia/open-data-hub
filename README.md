# Open Data Hub

[![CI](https://github.com/JaimeOnaindia/open-data-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/JaimeOnaindia/open-data-hub/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

Plataforma colaborativa **multi-país** de datos públicos abiertos. Cada país aporta su instituto oficial; el hub los unifica detrás de una API JSON común y un dashboard web.

> **Estado:** v1 funcional con 🇪🇸 España (INE) — criminalidad, IPC, paro y demografía. Listo para sumar países.

## Stack

- **Backend:** FastAPI + httpx + tenacity + pandas + pydantic v2 (Python 3.11+).
- **Frontend:** React 18 + Vite (TypeScript en migración).
- **Calidad:** ruff + mypy strict + pytest + respx + eslint.

## Estructura

```
backend/src/open_data_hub/
├── api.py                       # FastAPI app + endpoints JSON
├── core/                        # registry + tipos compartidos entre países
│   ├── datasets.py              # DatasetViewConfig (contrato común)
│   └── registry.py              # COUNTRIES (metadata)
└── countries/
    ├── es/                      # 🇪🇸 España
    │   └── sources/
    │       ├── ine_client.py    # cliente tempus3 del INE
    │       ├── crime.py         # criminalidad
    │       └── ine_datasets.py  # IPC, paro, demografía + ES_DATASET_VIEWS
    └── ...                      # añade tu país aquí

frontend/
├── index.html
└── src/main.js                  # dashboard React (TS en migración)

docs/adr/                        # decisiones arquitectónicas
tests/                           # pytest + respx
```

## Quickstart

Requisitos: Python 3.12 (vía `pyenv` recomendado), Node 20, `make`.

```bash
git clone https://github.com/JaimeOnaindia/open-data-hub.git
cd open-data-hub
python3.12 -m venv .venv
source .venv/bin/activate
make install
```

Levantar todo:

```bash
make api    # http://localhost:8000  (docs en /docs)
make front  # http://localhost:5173
```

Verificar:

```bash
make check  # mypy + ruff + tsc + eslint
pytest -q   # tests backend
```

## API

Todos los endpoints devuelven JSON. Docs auto-generadas en `/docs` (Swagger) y `/redoc`.

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/health` | Health check. |
| `GET /api/countries` | Catálogo de países y sus datasets. |
| `GET /api/datasets` | Índice plano de todos los datasets registrados. |
| `GET /api/datasets/{cc}/{dataset}/views` | Vistas disponibles de un dataset. |
| `GET /api/datasets/{cc}/{dataset}/views/{view}?nult=N` | Datos tidy de la vista. |

## Fuentes de datos actuales

### 🇪🇸 España — INE

API tempus3: `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{id}`

| Dataset | Tabla(s) | Fuente |
|---------|----------|--------|
| Criminalidad | 25997, 25998, 26014, 25698, 28716 | [Estadística de Condenados](https://www.ine.es/dynt3/inebase/es/index.htm?padre=2399) |
| Precios | 50902 | IPC por grupos ECOICOP |
| Mercado laboral | 74999 | Tasas de paro por edad/sexo/CCAA |
| Demografía | 73559, 73758 | Esperanza de vida + fenómenos demográficos |

## Cómo contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Resumen para añadir un país:

1. `backend/src/open_data_hub/countries/<cc>/sources/` con cliente HTTP + fetchers.
2. Registrar en `core/registry.py:COUNTRIES`.
3. `DatasetViewConfig` en `<cc>_datasets.py`; registrar en `api.py:DATASET_VIEWS_BY_COUNTRY`.
4. Tests con `respx` + fixtures reales.
5. PR siguiendo la plantilla.

Buenos primeros issues: [`good first issue`](https://github.com/JaimeOnaindia/open-data-hub/labels/good%20first%20issue) (nuevo país, nuevo dataset).

## Roadmap

Visión: catálogo federado de datos públicos abiertos, multi-país, con UI comparativa y API estable consumible por terceros.

- **Fase 0 — Fundamentos** ✅ git, CI, CONTRIBUTING, ADRs.
- **Fase 1 — Cinturón de seguridad** 🚧 tests con respx + fixtures reales, pre-commit, badge de cobertura.
- **Fase 2 — Plataforma**: TS en frontend + router + librería gráficos, API `/api/v1/`, i18n, caché persistente con snapshots fallback.
- **Fase 3 — Expansión**: Francia (INSEE), Portugal (INE-PT), Eurostat / OECD / World Bank, mapas, atribución y licencias en cada respuesta.

Detalle en [docs/adr/](docs/adr/).

## Decisiones arquitectónicas

- [ADR-0001: Arquitectura base — FastAPI + React + módulos por país](docs/adr/0001-architecture-baseline.md)

## Licencia

Pendiente de decisión (ver [CONTRIBUTING.md](CONTRIBUTING.md)).
