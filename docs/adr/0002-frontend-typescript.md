# ADR-0002: Frontend en TypeScript con router, TanStack Query y Recharts

- **Status:** aceptado
- **Fecha:** 2026-05-24
- **Decisores:** @JaimeOnaindia

## Contexto

El frontend v1 era un único `main.js` (440 LOC) en JS plano con `// @ts-check`, que:

- Renderizaba con `React.createElement` (sin JSX).
- Dibujaba un SVG de líneas a mano (~120 LOC) que no escalaba a otros tipos de gráfico.
- Consumía solo los endpoints legacy `/api/crime/*`, hardcodeando España.
- No tenía routing: no se podían compartir enlaces a una vista concreta.
- Mezclaba fetching, estado y presentación en un solo componente.

Para una plataforma multi-país a largo plazo necesitamos tipos reales, navegación por país/dataset, y una librería de gráficos extensible.

## Decisión

- **TypeScript estricto** (`strict`, `noUnusedLocals`, `exactOptionalPropertyTypes`, …) con JSX (`react-jsx`).
- **react-router-dom v6**: rutas `/` (catálogo) y `/:countryCode/:datasetKey` (dataset). La vista y el número de años (`nult`) viven en query params → enlaces compartibles.
- **TanStack Query v5**: fetching declarativo con caché, dedup y estados loading/error. `staleTime` 1h (los datos oficiales cambian poco).
- **Recharts v3**: reemplaza el SVG manual. `ResponsiveContainer` + `LineChart`. v3 (no v2) por estar activamente mantenida.
- **Consumo de endpoints genéricos** `/api/datasets/{cc}/{ds}/views[/{view}]` en vez del legacy `/api/crime/*`. El catálogo se construye desde `/api/countries`.
- **Separación de capas**: `api/` (cliente + hooks), `lib/transform.ts` (puro: filtros, pivot, CSV), `components/` (presentación), `pages/` (composición).

## Alternativas consideradas

- **Mantener JS + `@ts-check`:** menor coste inmediato pero sin garantías reales de tipo y difícil de escalar. Descartado.
- **visx en vez de Recharts:** más flexible (D3 de bajo nivel) pero mucho más verboso. Recharts cubre el 90% de necesidades con menos código. Reconsiderable si añadimos mapas/coropletas.
- **SWR en vez de TanStack Query:** equivalente y más ligero, pero TanStack tiene mejor tooling (devtools, mutaciones) para cuando crezca. Aceptamos el peso extra.
- **Sin librería de fetching (custom hooks):** lo que había; no merece la pena reimplementar caché/dedup.

## Consecuencias

**Positivas:**
- Tipos compartidos con el contrato API (`src/types.ts` espeja los modelos pydantic).
- Navegación real y enlaces compartibles.
- Gráficos extensibles (barras, áreas, etc. sin reescribir SVG).
- Frontend ya es multi-país (lee el catálogo dinámicamente).

**Negativas / deuda:**
- Bundle de charts ~365 kB (108 kB gzip). Mitigado con `manualChunks`; pendiente lazy-load del chart si crece.
- `src/types.ts` se mantiene a mano sincronizado con pydantic. Futuro: generar desde el OpenAPI del backend (ver ADR-0003).
- Producción necesita SPA fallback (rewrite a `index.html`) en el host estático.

## Seguimiento

- ADR-0003: versionar API `/api/v1/` + generar tipos TS desde OpenAPI.
- Tests de frontend (Vitest + Testing Library) — aún no hay.
- i18n del frontend (ADR-0005).
