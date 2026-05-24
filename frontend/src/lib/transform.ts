// Transformaciones puras de datos para el dashboard. Sin dependencias de React.

import type { DataRecord, DatasetTablePayload } from "../types";

export interface FilterDef {
  key: string;
  label: string;
  options: string[];
  defaults: string[];
}

export type FilterValues = Record<string, string[]>;

/** Fila pivotada para Recharts: { year, [categoría]: valor, ... }. */
export type ChartDatum = { year: number } & Record<string, number>;

export interface ChartData {
  categories: string[];
  categoryCount: number;
  years: number[];
  data: ChartDatum[];
  records: DataRecord[];
}

const FILTER_LABELS: Record<string, string> = {
  category: "Categoría",
  metric: "Métrica",
  nationality: "Nacionalidad",
  num_offenses: "Nº de delitos",
  sex: "Sexo",
  age_group: "Grupo de edad",
  territory: "Territorio",
  operation: "Operación",
};

const MAX_CATEGORIES = 8;

const PALETTE = [
  "#2563eb",
  "#059669",
  "#dc2626",
  "#7c3aed",
  "#ea580c",
  "#0891b2",
  "#4d7c0f",
  "#be123c",
];

export function filterLabel(key: string): string {
  return FILTER_LABELS[key] ?? key;
}

export function colorFor(value: string): string {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = value.charCodeAt(i) + ((hash << 5) - hash);
  }
  return PALETTE[Math.abs(hash) % PALETTE.length];
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0 }).format(value);
}

function defaultFilterValues(options: string[]): string[] {
  const preferred = options.find((option) => /dato base|total/i.test(option));
  return preferred ? [preferred] : options.slice(0, 1);
}

export function buildFilters(payload: DatasetTablePayload | undefined): FilterDef[] {
  if (!payload?.records.length) {
    return [];
  }
  return payload.view.filter_cols
    .map((key): FilterDef => {
      const options = [
        ...new Set(
          payload.records
            .map((record) => record[key])
            .filter((v): v is string | number => v !== null && v !== undefined && v !== "")
            .map(String),
        ),
      ].sort((a, b) => a.localeCompare(b, "es"));
      return { key, label: filterLabel(key), options, defaults: defaultFilterValues(options) };
    })
    .filter((filter) => filter.options.length > 1);
}

export function buildChart(
  payload: DatasetTablePayload | undefined,
  filters: FilterValues,
): ChartData {
  const empty: ChartData = { categories: [], categoryCount: 0, years: [], data: [], records: [] };
  if (!payload?.records.length) {
    return empty;
  }

  const { category_col: categoryCol, filter_cols: filterCols } = payload.view;
  const records = payload.records.filter((record) =>
    filterCols.every((key) => {
      const selected = filters[key] ?? [];
      return selected.length === 0 || selected.includes(String(record[key]));
    }),
  );

  const rows = records
    .filter((row) => {
      const value = row.value;
      return row[categoryCol] != null && typeof value === "number" && Number.isFinite(value);
    })
    .map((row) => ({
      category: String(row[categoryCol]),
      year: Number(row.year),
      value: Number(row.value),
    }));

  const totals = new Map<string, number>();
  for (const row of rows) {
    totals.set(row.category, (totals.get(row.category) ?? 0) + row.value);
  }
  const categories = [...totals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, MAX_CATEGORIES)
    .map(([category]) => category);

  const years = [...new Set(rows.map((row) => row.year))].sort((a, b) => a - b);
  const categorySet = new Set(categories);

  const byYear = new Map<number, ChartDatum>();
  for (const year of years) {
    byYear.set(year, { year });
  }
  for (const row of rows) {
    if (!categorySet.has(row.category)) {
      continue;
    }
    const datum = byYear.get(row.year);
    if (datum) {
      datum[row.category] = (datum[row.category] ?? 0) + row.value;
    }
  }

  return {
    categories,
    categoryCount: totals.size,
    years,
    data: years.map((year) => byYear.get(year) as ChartDatum),
    records,
  };
}

export function downloadCsv(records: DataRecord[], fileName: string): void {
  if (!records.length) {
    return;
  }
  const columns = [...new Set(records.flatMap((record) => Object.keys(record)))];
  const cell = (value: string | number | null): string =>
    `"${(value == null ? "" : String(value)).replaceAll('"', '""')}"`;
  const lines = [
    columns.join(","),
    ...records.map((record) => columns.map((column) => cell(record[column])).join(",")),
  ];
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}
