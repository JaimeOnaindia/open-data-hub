// @ts-check

import { createElement as h, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";

/** @type {Window & { OPEN_DATA_HUB_API_URL?: string }} */
const runtimeWindow = window;
const API_URL = runtimeWindow.OPEN_DATA_HUB_API_URL ?? "http://localhost:8000";
const DEFAULT_VIEW = "offenses-by-type";
const FILTER_LABELS = {
  category: "Categoría",
  metric: "Métrica",
  nationality: "Nacionalidad",
  num_offenses: "Nº de delitos",
  sex: "Sexo",
};

function App() {
  const [views, setViews] = useState([]);
  const [viewKey, setViewKey] = useState(DEFAULT_VIEW);
  const [years, setYears] = useState(10);
  const [payload, setPayload] = useState(null);
  const [filterValues, setFilterValues] = useState({});
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchJson("/api/crime/views")
      .then((data) => setViews(data))
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    setStatus("loading");
    setError("");
    setPayload(null);
    fetchJson(`/api/crime/views/${viewKey}?nult=${years}`)
      .then((data) => {
        setPayload(data);
        setStatus("ready");
      })
      .catch((err) => {
        setError(err.message);
        setStatus("error");
      });
  }, [viewKey, years]);

  const filters = useMemo(() => buildFilters(payload), [payload]);
  useEffect(() => {
    setFilterValues(Object.fromEntries(filters.map((filter) => [filter.key, filter.defaults])));
  }, [filters]);

  const chart = useMemo(() => buildChart(payload, filterValues), [payload, filterValues]);
  const latestYear = chart.years.at(-1);
  const totalLatest = latestYear
    ? chart.rows
        .filter((row) => row.year === latestYear)
        .reduce((total, row) => total + row.value, 0)
    : 0;

  return h(
    "main",
    { className: "app-shell" },
    h(
      "aside",
      { className: "sidebar" },
      h("div", { className: "brand" }, h("span", { className: "brand-mark" }, "OD"), h("span", null, "Open Data Hub")),
      h("p", { className: "muted" }, "España · INE · criminalidad"),
      h(
        "label",
        null,
        "Vista",
        h(
          "select",
          { value: viewKey, onChange: (event) => setViewKey(event.target.value) },
          views.map((view) => h("option", { key: view.key, value: view.key }, view.label)),
        ),
      ),
    ),
    h(
      "section",
      { className: "content" },
      h(
        "div",
        { className: "topbar" },
        h(
          "div",
          null,
          h("h1", null, payload?.view.label ?? "Criminalidad en España"),
          h(
            "p",
            { className: "muted" },
            "Frontend React sobre una API JSON propia. Los datos siguen viniendo en directo del INE.",
          ),
        ),
      ),
      h(
        "div",
        { className: "toolbar" },
        h(
          "label",
          null,
          "Años",
          h("input", {
            type: "range",
            min: "2",
            max: "20",
            value: years,
            onChange: (event) => setYears(Number(event.target.value)),
          }),
        ),
        h(
          "div",
          { className: "filters" },
          filters.map((filter) =>
            h(FilterSelect, {
              filter,
              key: filter.key,
              value: filterValues[filter.key] ?? [],
              onChange: (value) =>
                setFilterValues((current) => ({ ...current, [filter.key]: value })),
            }),
          ),
        ),
        h(
          "button",
          {
            className: "button",
            disabled: chart.records.length === 0,
            onClick: () => downloadCsv(chart.records, `${viewKey}_${years}_years.csv`),
            type: "button",
          },
          "Descargar CSV",
        ),
        h("strong", null, `${years} años`),
      ),
      status === "loading" ? h("div", { className: "status" }, "Cargando datos del INE...") : null,
      status === "error" ? h("div", { className: "error" }, error) : null,
      status === "ready"
        ? [
            h(
              "section",
              { className: "metrics", key: "metrics" },
              h(Metric, {
                label: `Total registrado (${latestYear ?? "-"})`,
                value: formatNumber(totalLatest),
              }),
              h(Metric, { label: "Años disponibles", value: chart.years.length }),
              h(Metric, { label: payload.view.category_label, value: chart.categoryCount }),
            ),
            h(
              "section",
              { className: "panel", key: "chart" },
              h(
                "div",
                { className: "panel-header" },
                h(
                  "div",
                  null,
                  h("strong", null, "Evolución temporal"),
                  h("p", { className: "muted" }, "Top 8 categorías por valor acumulado."),
                ),
              ),
              chart.rows.length > 0
                ? h(TrendChart, { chart })
                : h("div", { className: "empty-state" }, "No hay datos para estos filtros."),
            ),
          ]
        : null,
    ),
  );
}

function FilterSelect({ filter, value, onChange }) {
  return h(
    "label",
    null,
    filter.label,
    h(
      "select",
      {
        multiple: true,
        value,
        onChange: (event) =>
          onChange([...event.target.selectedOptions].map((option) => option.value)),
      },
      filter.options.map((option) => h("option", { key: option, value: option }, option)),
    ),
  );
}

function Metric({ label, value }) {
  return h(
    "article",
    { className: "metric" },
    h("span", { className: "muted" }, label),
    h("strong", null, value),
  );
}

function TrendChart({ chart }) {
  const width = 960;
  const height = 420;
  const margin = { top: 24, right: 28, bottom: 44, left: 86 };
  const valueMap = new Map();

  for (const row of chart.rows) {
    const key = chartKey(row.category, row.year);
    valueMap.set(key, (valueMap.get(key) ?? 0) + row.value);
  }

  const valueFor = (category, year) => valueMap.get(chartKey(category, year)) ?? 0;
  const maxValue = Math.max(
    1,
    ...chart.categories.flatMap((category) =>
      chart.years.map((year) => valueFor(category, year)),
    ),
  );
  const xFor = (year) => {
    const index = chart.years.indexOf(year);
    const denominator = Math.max(1, chart.years.length - 1);
    return margin.left + (index / denominator) * (width - margin.left - margin.right);
  };
  const yFor = (value) =>
    margin.top + (1 - value / maxValue) * (height - margin.top - margin.bottom);
  const yearTicks = [...new Set([chart.years[0], chart.years[Math.floor(chart.years.length / 2)], chart.years.at(-1)])]
    .filter(Boolean);
  const valueTicks = [0, maxValue / 2, maxValue];

  return h(
    "div",
    { className: "chart-frame" },
    h(
      "svg",
      { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": "Evolución temporal" },
      h("line", {
        x1: margin.left,
        y1: height - margin.bottom,
        x2: width - margin.right,
        y2: height - margin.bottom,
        stroke: "#d0d5dd",
      }),
      h("line", {
        x1: margin.left,
        y1: margin.top,
        x2: margin.left,
        y2: height - margin.bottom,
        stroke: "#d0d5dd",
      }),
      valueTicks.map((tick) =>
        h(
          "g",
          { key: `y-${tick}` },
          h("line", {
            x1: margin.left,
            y1: yFor(tick),
            x2: width - margin.right,
            y2: yFor(tick),
            stroke: "#f2f4f7",
          }),
          h(
            "text",
            {
              x: margin.left - 12,
              y: yFor(tick) + 4,
              textAnchor: "end",
              fill: "#667085",
              fontSize: 12,
            },
            formatNumber(tick),
          ),
        ),
      ),
      yearTicks.map((year) =>
        h(
          "text",
          {
            key: `x-${year}`,
            x: xFor(year),
            y: height - 12,
            textAnchor: "middle",
            fill: "#667085",
            fontSize: 12,
          },
          year,
        ),
      ),
      chart.categories.map((category) =>
        h(
          "polyline",
          {
            key: category,
            points: chart.years
              .map((year) => `${xFor(year)},${yFor(valueFor(category, year))}`)
              .join(" "),
            fill: "none",
            stroke: colorFor(category),
            strokeWidth: 2.5,
            strokeLinejoin: "round",
            strokeLinecap: "round",
          },
          h("title", null, category),
        ),
      ),
    ),
    h(
      "div",
      { className: "chart-legend" },
      chart.categories.map((category) =>
        h(
          "span",
          { className: "legend-item", key: category },
          h("span", {
            className: "legend-swatch",
            style: { backgroundColor: colorFor(category) },
          }),
          category,
        ),
      ),
    ),
  );
}

async function fetchJson(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: no se pudo leer ${path}`);
  }
  return response.json();
}

function buildFilters(payload) {
  if (!payload?.records.length) {
    return [];
  }

  return payload.view.filter_cols
    .map((key) => {
      const options = [...new Set(payload.records.map((record) => record[key]).filter(Boolean))]
        .map(String)
        .sort((a, b) => a.localeCompare(b, "es"));
      return {
        defaults: defaultFilterValues(options),
        key,
        label: FILTER_LABELS[key] ?? key,
        options,
      };
    })
    .filter((filter) => filter.options.length > 1);
}

function defaultFilterValues(options) {
  const preferred = options.find((option) => /dato base|total/i.test(option));
  return preferred ? [preferred] : options.slice(0, 1);
}

function buildChart(payload, filters) {
  if (!payload?.records.length) {
    return { categories: [], categoryCount: 0, records: [], rows: [], years: [] };
  }

  const categoryCol = payload.view.category_col;
  const records = payload.records.filter((record) =>
    payload.view.filter_cols.every((key) => {
      const selected = filters[key] ?? [];
      return selected.length === 0 || selected.includes(String(record[key]));
    }),
  );
  const rows = records
    .filter((row) => row[categoryCol] && Number.isFinite(row.value))
    .map((row) => ({
      category: String(row[categoryCol]),
      year: Number(row.year),
      value: Number(row.value),
    }));
  const totals = rows.reduce((acc, row) => {
    acc.set(row.category, (acc.get(row.category) ?? 0) + row.value);
    return acc;
  }, new Map());
  const categories = [...totals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([category]) => category);
  const years = [...new Set(rows.map((row) => row.year))].sort((a, b) => a - b);
  return { categories, categoryCount: totals.size, records, rows, years };
}

function chartKey(category, year) {
  return `${category}__${year}`;
}

function colorFor(value) {
  const palette = [
    "#2563eb",
    "#059669",
    "#dc2626",
    "#7c3aed",
    "#ea580c",
    "#0891b2",
    "#4d7c0f",
    "#be123c",
  ];
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = value.charCodeAt(index) + ((hash << 5) - hash);
  }
  return palette[Math.abs(hash) % palette.length];
}

function formatNumber(value) {
  return new Intl.NumberFormat("es-ES", { maximumFractionDigits: 0 }).format(value);
}

function downloadCsv(records, fileName) {
  if (!records.length) {
    return;
  }

  const columns = [...new Set(records.flatMap((record) => Object.keys(record)))];
  const lines = [
    columns.join(","),
    ...records.map((record) =>
      columns.map((column) => csvCell(record[column])).join(","),
    ),
  ];
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function csvCell(value) {
  const text = value == null ? "" : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

createRoot(document.getElementById("root")).render(h(App));
