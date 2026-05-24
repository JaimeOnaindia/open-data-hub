# Open Data Hub

[![CI](https://github.com/JaimeOnaindia/open-data-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/JaimeOnaindia/open-data-hub/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

Plataforma colaborativa **multi-país** de datos públicos abiertos. Cada país aporta su instituto oficial; el hub los unifica detrás de una API JSON común y un dashboard web.

> **Estado:** v1 funcional con 🇪🇸 España (INE) — criminalidad, IPC, paro y demografía. Listo para sumar países.

## Stack

- **Backend:** FastAPI + httpx + tenacity + pandas + pydantic v2 (Python 3.11+).
- **Frontend:** React 18 + TypeScript + Vite, react-router, TanStack Query, Recharts, i18n es/en.
- **Calidad:** ruff + mypy strict + pytest + respx (backend); eslint + tsc strict + Vitest + Testing Library (frontend).

## Estructura

```
backend/src/open_data_hub/
├── api.py                       # FastAPI app + endpoints JSON (agnóstico de país)
├── core/                        # tipos compartidos entre proveedores
│   ├── datasets.py              # DatasetViewConfig (contrato común)
│   └── registry.py              # modelos CountryConfig / DatasetConfig
└── countries/
    ├── catalog.py               # _PROVIDERS → COUNTRIES + DATASET_VIEWS_BY_COUNTRY
    ├── es/                      # 🇪🇸 España (INE) — expone COUNTRY + VIEWS
    │   └── sources/
    │       ├── ine_client.py    # cliente tempus3 del INE
    │       ├── crime.py         # criminalidad
    │       └── ine_datasets.py  # IPC, paro, demografía + ES_DATASET_VIEWS
    ├── eu/                      # 🇪🇺 Eurostat (multi-país, JSON-stat 2.0)
    │   └── sources/
    │       ├── eurostat_client.py    # cliente + parse_jsonstat (reutilizable)
    │       └── eurostat_datasets.py  # paro + IPCA por país + EU_DATASET_VIEWS
    └── ...                      # añade tu país aquí

frontend/
├── index.html
└── src/
    ├── main.tsx                 # entrypoint: router + QueryClient
    ├── App.tsx                  # layout + sidebar
    ├── api/                     # cliente fetch tipado + hooks TanStack Query
    ├── components/              # TrendChart (Recharts), FilterSelect, Metric, Sidebar
    ├── lib/transform.ts         # transformaciones puras (filtros, pivot, CSV)
    └── pages/                   # CatalogPage, DatasetPage

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

Contrato estable bajo **`/api/v1`**. Todos los endpoints devuelven JSON; aceptan `?lang=es|en`.
Docs auto-generadas en `/docs` (Swagger) y `/redoc`. Las rutas `/api/*` (sin `v1`) y `/api/crime/*`
siguen activas como **alias deprecados** (se eliminarán en v2).

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/v1/health` | Health check. |
| `GET /api/v1/countries` | Catálogo de países y sus datasets. |
| `GET /api/v1/datasets` | Índice plano de todos los datasets registrados. |
| `GET /api/v1/datasets/{cc}/{dataset}/views` | Vistas disponibles de un dataset. |
| `GET /api/v1/datasets/{cc}/{dataset}/views/{view}?nult=N` | Datos tidy de la vista. |

Los tipos del frontend se generan desde el OpenAPI del backend (`frontend/src/api/schema.ts`):
ejecuta `make types` tras cambiar cualquier modelo/endpoint. CI falla si quedan desincronizados.

## Persistencia de datos

La API **no llama a las fuentes oficiales en cada petición**: sirve desde snapshots propios.

- **Ingesta** (`make ingest`): recorre el catálogo, reutiliza los mismos `fetch_*` y guarda
  cada vista en `data/snapshots/<cc>/<dataset>/<view>.parquet` con un sidecar `.meta.json`
  de procedencia (`source`, `fetched_at`, filas). Hace peticiones en vivo → se corre a mano
  o por cron, nunca en tests/CI.
- **Servicio**: la API lee el parquet (`core/storage.py`) y filtra los últimos `nult` años.
  Si una vista aún no se ha ingestado, cae a la fuente en vivo (cómodo en desarrollo).
- **Resiliencia**: si el INE/Eurostat cae o cambia formato, la ingesta falla pero la web
  sigue sirviendo el último snapshot bueno.

`data/snapshots/` está en `.gitignore` (no versionamos datos). Almacenamiento elegido:
parquet por simplicidad; el grano tidy alimenta directamente un futuro modelo relacional/warehouse.

## Fuentes de datos actuales

### 🇪🇸 España — INE

API tempus3: `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{id}`

| Dataset | Tabla(s) | Fuente |
|---------|----------|--------|
| Criminalidad | 25997, 25998, 26014, 25698, 28716 | [Estadística de Condenados](https://www.ine.es/dynt3/inebase/es/index.htm?padre=2399) |
| Precios | 50902 | IPC por grupos ECOICOP |
| Mercado laboral | 74999 | Tasas de paro por edad/sexo/CCAA |
| Demografía | 73559, 73758 | Esperanza de vida + fenómenos demográficos |

### 🇪🇺 Unión Europea — Eurostat

API de difusión (JSON-stat 2.0): `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}`

| Dataset | Código Eurostat | Fuente |
|---------|-----------------|--------|
| Mercado laboral | `une_rt_a` | Tasa de paro anual comparada por país |
| Precios | `prc_hicp_aind` | IPCA — variación anual media por país |

El parser `parse_jsonstat` es reutilizable para cualquier fuente JSON-stat 2.0 (PxStat, CSO Irlanda, SSB Noruega…).

## Cómo contribuir

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Resumen para añadir un país:

1. `backend/src/open_data_hub/countries/<cc>/sources/` con cliente HTTP + fetchers tidy.
2. `countries/<cc>/__init__.py` expone `COUNTRY` (CountryConfig) y `VIEWS`.
3. Registra el proveedor en `countries/catalog.py` (`_PROVIDERS`) — única edición en código compartido.
4. Tests con `respx` + fixtures reales.
5. PR siguiendo la plantilla.

La API y el frontend recogen el proveedor automáticamente desde el catálogo.

Buenos primeros issues: [`good first issue`](https://github.com/JaimeOnaindia/open-data-hub/labels/good%20first%20issue) (nuevo país, nuevo dataset).

## Roadmap

Visión: catálogo federado de datos públicos abiertos, multi-país, con UI comparativa y API estable consumible por terceros.

- **Fase 0 — Fundamentos** ✅ git, CI, CONTRIBUTING, ADRs.
- **Fase 1 — Cinturón de seguridad** ✅ tests con respx + fixtures reales (96% cobertura), pre-commit.
- **Fase 2 — Plataforma** 🚧 frontend TS + router + Recharts ✅; i18n es/en (API `?lang=` + toggle) ✅; pendiente API `/api/v1/`, caché persistente con snapshots fallback.
- **Fase 3 — Expansión** 🚧 Eurostat (multi-país, JSON-stat) ✅; persistencia parquet + ingesta propia ✅; pendiente Francia (INSEE), Portugal (INE-PT), OECD / World Bank, mapas, atribución y licencias en cada respuesta.

Detalle en [docs/adr/](docs/adr/).

## Decisiones arquitectónicas

- [ADR-0001: Arquitectura base — FastAPI + React + módulos por país](docs/adr/0001-architecture-baseline.md)
- [ADR-0002: Frontend en TypeScript con router, TanStack Query y Recharts](docs/adr/0002-frontend-typescript.md)
- [ADR-0003: Fuentes multilaterales y registro de proveedores en catálogo](docs/adr/0003-multilateral-sources.md)

## Licencia

Pendiente de decisión (ver [CONTRIBUTING.md](CONTRIBUTING.md)).
