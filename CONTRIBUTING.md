# Contribuir a Open Data Hub

> English-friendly: this guide is bilingual. If a section is only in Spanish, ask in an issue and we'll translate it.

¡Gracias por querer contribuir! Open Data Hub es una plataforma colaborativa para servir datos públicos abiertos de cualquier país a través de una API unificada y un dashboard común. Necesitamos personas que conozcan los institutos oficiales de su país y su API.

## Tabla de contenidos

- [Formas de contribuir](#formas-de-contribuir)
- [Setup local](#setup-local)
- [Añadir un país nuevo](#añadir-un-país-nuevo)
- [Añadir un dataset a un país existente](#añadir-un-dataset-a-un-país-existente)
- [Estilo de código](#estilo-de-código)
- [Tests](#tests)
- [Flujo de PR](#flujo-de-pr)
- [Decisiones de arquitectura (ADR)](#decisiones-de-arquitectura-adr)

## Formas de contribuir

- **Añadir un país nuevo** con su instituto oficial de estadística (INSEE 🇫🇷, INE-PT 🇵🇹, ISTAT 🇮🇹, Destatis 🇩🇪, ONS 🇬🇧, IBGE 🇧🇷, INEGI 🇲🇽, …).
- **Añadir un dataset** a un país existente (educación, salud, energía, medio ambiente…).
- **Mejorar visualizaciones** del frontend (mapas, gráficos comparativos, accesibilidad).
- **Traducciones** (i18n de labels, descripciones, documentación).
- **Tests y fixtures** — captura snapshots reales de APIs oficiales.
- **Documentación** — guías, ADRs, ejemplos.

## Setup local

Requisitos:

- Python 3.12 (recomendado vía `pyenv`).
- Node.js 20 o superior.
- `make`.

```bash
git clone https://github.com/JaimeOnaindia/open-data-hub.git
cd open-data-hub
python3.12 -m venv .venv
source .venv/bin/activate
make install
```

Levantar todo en local:

```bash
make api    # backend en http://localhost:8000
make front  # frontend en http://localhost:5173
```

Verificar antes de hacer commit:

```bash
make check  # mypy + ruff + tsc + eslint
pytest -q   # tests
```

(Opcional pero recomendado) activar **pre-commit** para que se ejecute automáticamente:

```bash
pip install pre-commit
pre-commit install
```


## Añadir un país nuevo

Convención: códigos ISO 3166-1 alpha-2 en minúsculas (`es`, `fr`, `pt`, `de`, …).

1. Crea la carpeta `backend/src/open_data_hub/countries/<cc>/sources/`.
2. Implementa un **cliente HTTP** para la API oficial (ejemplos: `ine_client.py` para España, `eurostat_client.py` para Eurostat). Debe usar `httpx` + `tenacity` para reintentos. Si la fuente sirve **JSON-stat 2.0** (Eurostat, PxStat, CSO Irlanda, SSB Noruega…), reutiliza `parse_jsonstat`.
3. Implementa funciones `fetch_*` que devuelvan `pandas.DataFrame` **tidy** con como mínimo las columnas:
   - `year: int`
   - `value: float`
   - una o más columnas de dimensión (territorio, sexo, edad, categoría…).
4. Crea las `DatasetViewConfig` en `countries/<cc>/sources/<cc>_datasets.py`.
5. En `countries/<cc>/__init__.py` expón dos símbolos: `COUNTRY` (un `CountryConfig`) y `VIEWS` (el dict de views).
6. Registra el proveedor en `countries/catalog.py`: importa `COUNTRY`/`VIEWS` y añade la tupla a `_PROVIDERS`. **Es la única edición en código compartido** → sin conflictos con otros países.
7. Añade tests con `respx` mockeando la API oficial. Incluye al menos un fixture real (ver `tests/fixtures/`).
8. Actualiza el README con la fuente y enlace al catálogo.

La API y el frontend recogen el nuevo proveedor **automáticamente** desde el catálogo; no hay que tocar `api.py` ni el frontend.

## Añadir un dataset a un país existente

1. Añade el fetcher en el módulo `sources/` correspondiente.
2. Añade el `DatasetConfig` a `COUNTRY.datasets` (en `countries/<cc>/__init__.py`) y la `DatasetViewConfig` al dict `VIEWS` del país.
3. Tests + fixture.

## Estilo de código

**Backend (Python):**
- `ruff` con reglas `E, F, I, B, UP, SIM` (ver `pyproject.toml`).
- `mypy --strict`. Sin `Any` salvo en boundaries justificados.
- Imports ordenados (ruff `I`).
- Type hints obligatorios en toda función pública.

**Frontend (TypeScript):**
- TS estricto. Nuevos archivos en `.ts`/`.tsx`.
- `eslint` recomendado + `@typescript-eslint`.
- React 18 con hooks. Sin clases.
- Los tipos del contrato API (`src/api/schema.ts`) se **generan** desde el OpenAPI del backend.
  No los edites a mano: tras cambiar un modelo o endpoint ejecuta `make types` y commitea
  `frontend/openapi.json` + `frontend/src/api/schema.ts`. CI verifica que no haya drift.

## Tests

```bash
.venv/bin/pytest                       # backend
npm --prefix frontend test             # frontend (cuando esté configurado)
```

Reglas:
- Tests de fetchers usan `respx` con fixtures JSON capturados de APIs reales (no llamamos al INE/INSEE/etc. desde tests).
- Cobertura mínima objetivo: 80% en `backend/src/open_data_hub/`.

## Flujo de PR

1. **Fork** y rama desde `main`: `git checkout -b feat/<cc>-<tema>`.
2. Commits atómicos. Mensaje en imperativo: `add fr/INSEE consumer prices fetcher`.
3. `make check` debe pasar antes de empujar.
4. Abre PR contra `main` siguiendo la plantilla.
5. Espera revisión. Para cambios grandes (nuevo país, refactor de `core/`) abre un **issue de propuesta** antes.

Convenciones de commit (opcionales pero apreciadas):
- `feat:` nueva funcionalidad / país / dataset
- `fix:` bugfix
- `docs:` documentación
- `refactor:` cambio sin afectar comportamiento
- `test:` solo tests
- `chore:` build, CI, deps

## Decisiones de arquitectura (ADR)

Cambios estructurales (nueva capa, cambio de stack, contrato API) se discuten en `docs/adr/NNNN-<slug>.md` antes de implementarse. Template: ver `docs/adr/0000-template.md`.

## Código de conducta

Este proyecto adopta el [Contributor Covenant](CODE_OF_CONDUCT.md). Sé respetuoso o no estás aquí.

## Licencia

Pendiente de decisión. Hasta entonces, contribuciones se asumen bajo el principio de que el autor original puede relicenciar el proyecto en el futuro.
