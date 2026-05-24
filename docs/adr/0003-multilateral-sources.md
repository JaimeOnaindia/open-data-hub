# ADR-0003: Fuentes multilaterales y registro de proveedores en catálogo

- **Status:** aceptado
- **Fecha:** 2026-05-24
- **Decisores:** @JaimeOnaindia

## Contexto

El hub nació modelando "país → datasets" con institutos nacionales. Pero buena parte de los datos abiertos comparables entre países vienen de **fuentes multilaterales** (Eurostat, OECD, World Bank, ILO) que sirven muchos países en una sola API. Forzar un país por PR es lento; una sola integración de Eurostat aporta ~38 países.

Además, el registro de views estaba hardcodeado en `api.py` (`DATASET_VIEWS_BY_COUNTRY = {"es": ...}`), un punto de conflicto de merge cuando muchos colaboradores añaden países a la vez.

## Decisión

1. **Proveedor como entidad de primer nivel.** `CountryConfig` modela tanto institutos nacionales (`es`/INE) como fuentes multilaterales (`eu`/Eurostat). `code` admite ISO 3166-1 alpha-2 incluidas reservas excepcionales (`eu`). Una fuente multilateral expone la dimensión país (`geo`) como columna categórica → comparaciones entre países con la UI existente.

2. **Registro descentralizado.** Cada proveedor expone `COUNTRY` + `VIEWS` en su `__init__.py`. `countries/catalog.py` los agrega en `_PROVIDERS`. Añadir un proveedor = 1 tupla en `catalog.py`; `api.py` y el frontend no se tocan.

3. **Cliente JSON-stat reutilizable.** `parse_jsonstat` (en `eurostat_client.py`) parsea JSON-stat 2.0 genérico (índices dict o lista, valores dict sparse o array con nulls, decodificación row-major del hipercubo). Sirve para Eurostat y para futuras fuentes JSON-stat: PxStat (CSO Irlanda), SSB (Noruega), Statbank (Dinamarca).

## Alternativas consideradas

- **Refactor a `ProviderConfig` con `kind: national | multilateral`:** más correcto semánticamente, pero obliga a cambiar el contrato y los tipos del frontend. Aplazado; `CountryConfig` con `eu` cubre la necesidad ahora.
- **Eurostat vía SDMX-ML:** XML más complejo; JSON-stat es más simple y suficiente.
- **Descubrimiento dinámico de módulos país (pkgutil):** mágico y frágil para mypy/revisión. Preferimos el registro explícito en `catalog.py`.

## Consecuencias

**Positivas:**
- Eurostat aporta decenas de países europeos en dos datasets (paro `une_rt_a`, IPCA `prc_hicp_aind`).
- El frontend muestra el proveedor `eu` automáticamente (lee el catálogo).
- Añadir país ya no genera conflictos en `api.py`.
- `parse_jsonstat` abre la puerta a muchas fuentes nacionales JSON-stat con poco código.

**Negativas / deuda:**
- Conflación semántica país/proveedor (mitigada con docstring; ver futuro `ProviderConfig`).
- Los agregados de Eurostat (EU27, EA20…) aparecen como "países" en el gráfico. Aceptable; filtrables en el futuro.
- `geo` se renombra a `country` en la capa de dataset; el mapeo de etiquetas depende de `lang=EN` de Eurostat (i18n pendiente, ADR-0005).

## Seguimiento

- ADR-0005: i18n (idioma de etiquetas Eurostat e INE).
- Posible `ProviderConfig` con `kind` y metadatos de licencia/atribución por fuente.
- Más fuentes JSON-stat reutilizando `parse_jsonstat`.
