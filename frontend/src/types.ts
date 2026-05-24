// Tipos del contrato API. La forma de los metadatos se genera desde el OpenAPI del
// backend en `schema.ts` (single source of truth: pydantic → OpenAPI → TS).
// Regenerar con `make types` (o `npm run gen:types`). Aquí solo aliaseamos y afinamos
// los dos puntos que el OpenAPI deja deliberadamente laxos (records y filter_cols).

import type { components } from "./api/schema";

type Schemas = components["schemas"];

export type DatasetSummary = Schemas["DatasetSummary"];
export type CountrySummary = Schemas["CountrySummary"];
export type DatasetIndexItem = Schemas["DatasetIndexItem"];

// El backend siempre serializa filter_cols (lista, posiblemente vacía) → lo hacemos requerido.
export type DatasetViewSummary = Omit<Schemas["DatasetViewSummary"], "filter_cols"> & {
  filter_cols: string[];
};

/** Una observación tidy: dimensiones arbitrarias + year + value. */
export type DataRecord = Record<string, string | number | null>;

// records llega tipado como objetos libres ({[k]: unknown}); lo afinamos a nuestro contrato.
export type DatasetTablePayload = Omit<Schemas["DatasetTablePayload"], "view" | "records"> & {
  view: DatasetViewSummary;
  records: DataRecord[];
};
