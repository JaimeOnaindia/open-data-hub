# ADR-0001: Arquitectura base — FastAPI + React + módulos por país

- **Status:** aceptado
- **Fecha:** 2026-05-24
- **Decisores:** @JaimeOnaindia

## Contexto

Open Data Hub nace como portfolio personal y evoluciona hacia una plataforma colaborativa multi-país de datos abiertos. La v1 sirvió España (INE) sobre Streamlit; la v2 (mayo 2026) se reescribió como **API FastAPI + frontend React/Vite**.

Necesitamos un patrón que:

1. Permita a contribuyentes de cualquier país añadir su instituto oficial sin tocar código común.
2. Mantenga un contrato API estable independiente de la fuente.
3. Soporte tipado estricto (mypy strict + TypeScript) y CI sobre PRs externas.

## Decisión

- **Backend:** Python 3.12 + FastAPI + httpx + tenacity + pandas + pydantic v2. Servido con uvicorn.
- **Frontend:** React 18 + Vite. Migración a TypeScript en curso (ADR pendiente: 0002).
- **Estructura de países:** cada país vive aislado en `backend/src/open_data_hub/countries/<cc>/sources/`. Contrato: las funciones `fetch_*` devuelven `pandas.DataFrame` tidy con columnas obligatorias `year`, `value` y dimensiones opcionales.
- **Registro central:** `core/registry.py` declara metadatos (nombre, bandera, datasets disponibles). `core/datasets.py` define el contrato `DatasetViewConfig`.
- **API:** versionar bajo `/api/v1/` (ADR pendiente: 0003). Endpoints genéricos `/api/v1/datasets/{cc}/{dataset}/views/...`.

## Alternativas consideradas

- **Monolito Streamlit:** rápido para v1 pero acopla UI + datos y no soporta consumo programático. Descartado.
- **Dagster/Airflow + Postgres con medallion ETL:** demasiado peso para portfolio y bloquea contribuciones de no-dataengineers. Descartado (esta era la v0, eliminada).
- **Backend en Go/Rust:** mejor rendimiento pero excluye contribuyentes Python (que son los habituales en el dominio de datos públicos). Descartado.

## Consecuencias

**Positivas:**
- Onboarding de contribuyente nuevo se reduce a "copia la carpeta de un país existente, cambia el cliente HTTP".
- API consumible por terceros (notebooks, otros frontends, bots).
- Tipos fuertes en ambos lados reducen bugs en boundary.

**Negativas:**
- Coste de mantener dos stacks (Python + TS).
- Caché en proceso (`@lru_cache`) no escala — requerirá adopción de Redis o disk cache (ADR pendiente: 0004).
- Sin persistencia de snapshots, dependemos de la salud de las APIs oficiales.

**Seguimiento:**
- ADR-0002: Migración a TypeScript del frontend.
- ADR-0003: Versionado de API y deprecación de `/api/crime/*`.
- ADR-0004: Capa de caché y snapshots persistentes.
- ADR-0005: Internacionalización de labels y descripciones.
