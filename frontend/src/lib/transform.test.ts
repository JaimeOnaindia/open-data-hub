import { afterEach, describe, expect, it, vi } from "vitest";

import type { DataRecord, DatasetTablePayload, DatasetViewSummary } from "../types";
import {
  buildChart,
  buildFilters,
  colorFor,
  downloadCsv,
  filterLabel,
  formatNumber,
} from "./transform";

function makePayload(
  view: Partial<DatasetViewSummary>,
  records: DataRecord[],
): DatasetTablePayload {
  return {
    view: {
      key: "v",
      label: "V",
      category_col: "cat",
      category_label: "Cat",
      filter_cols: [],
      ...view,
    },
    records,
  };
}

describe("buildFilters", () => {
  it("returns [] for empty payload", () => {
    expect(buildFilters(undefined)).toEqual([]);
    expect(buildFilters(makePayload({}, []))).toEqual([]);
  });

  it("builds filters from filter_cols, sorted and deduped", () => {
    const payload = makePayload({ filter_cols: ["metric"] }, [
      { cat: "A", metric: "Tasa", year: 2024, value: 1 },
      { cat: "A", metric: "Dato base", year: 2024, value: 2 },
      { cat: "A", metric: "Dato base", year: 2023, value: 3 },
    ]);
    const filters = buildFilters(payload);
    expect(filters).toHaveLength(1);
    expect(filters[0].key).toBe("metric");
    expect(filters[0].options).toEqual(["Dato base", "Tasa"]);
  });

  it("defaults to the 'Dato base'/'Total' option when present", () => {
    const payload = makePayload({ filter_cols: ["metric"] }, [
      { cat: "A", metric: "Tasa", year: 2024, value: 1 },
      { cat: "A", metric: "Dato base", year: 2024, value: 2 },
    ]);
    expect(buildFilters(payload)[0].defaults).toEqual(["Dato base"]);
  });

  it("drops filters with a single option", () => {
    const payload = makePayload({ filter_cols: ["metric", "sex"] }, [
      { cat: "A", metric: "Dato base", sex: "Hombres", year: 2024, value: 1 },
      { cat: "A", metric: "Tasa", sex: "Mujeres", year: 2024, value: 2 },
      { cat: "A", metric: "Dato base", sex: "Hombres", year: 2023, value: 3 },
    ]);
    const keys = buildFilters(payload).map((f) => f.key);
    expect(keys).toContain("metric");
    expect(keys).toContain("sex");
    // 'cat' is not a filter_col, so never appears
    expect(keys).not.toContain("cat");
  });
});

describe("buildChart", () => {
  it("returns an empty structure for empty payload", () => {
    const chart = buildChart(undefined, {});
    expect(chart).toEqual({ categories: [], categoryCount: 0, years: [], data: [], records: [] });
  });

  it("pivots records into one datum per year keyed by category", () => {
    const payload = makePayload({ category_col: "cat" }, [
      { cat: "A", year: 2023, value: 10 },
      { cat: "B", year: 2023, value: 5 },
      { cat: "A", year: 2024, value: 12 },
      { cat: "B", year: 2024, value: 7 },
    ]);
    const chart = buildChart(payload, {});
    expect(chart.years).toEqual([2023, 2024]);
    expect(chart.data).toEqual([
      { year: 2023, A: 10, B: 5 },
      { year: 2024, A: 12, B: 7 },
    ]);
  });

  it("keeps only the top 8 categories but counts them all", () => {
    const records: DataRecord[] = Array.from({ length: 9 }, (_, i) => ({
      cat: `C${i}`,
      year: 2024,
      value: i + 1, // C8 highest, C0 lowest
    }));
    const chart = buildChart(makePayload({ category_col: "cat" }, records), {});
    expect(chart.categoryCount).toBe(9);
    expect(chart.categories).toHaveLength(8);
    expect(chart.categories).toContain("C8");
    expect(chart.categories).not.toContain("C0");
  });

  it("filters records by selected filter values", () => {
    const payload = makePayload({ category_col: "cat", filter_cols: ["metric"] }, [
      { cat: "A", metric: "Dato base", year: 2024, value: 10 },
      { cat: "A", metric: "Tasa", year: 2024, value: 99 },
    ]);
    const chart = buildChart(payload, { metric: ["Dato base"] });
    expect(chart.data).toEqual([{ year: 2024, A: 10 }]);
  });

  it("treats an empty selection as no filter", () => {
    const payload = makePayload({ category_col: "cat", filter_cols: ["metric"] }, [
      { cat: "A", metric: "Dato base", year: 2024, value: 10 },
      { cat: "A", metric: "Tasa", year: 2024, value: 5 },
    ]);
    const chart = buildChart(payload, { metric: [] });
    expect(chart.data).toEqual([{ year: 2024, A: 15 }]);
  });

  it("ignores rows with null or non-finite values", () => {
    const payload = makePayload({ category_col: "cat" }, [
      { cat: "A", year: 2024, value: null },
      { cat: "B", year: 2024, value: 8 },
    ]);
    const chart = buildChart(payload, {});
    expect(chart.categories).toEqual(["B"]);
    expect(chart.data).toEqual([{ year: 2024, B: 8 }]);
  });
});

describe("formatNumber", () => {
  it("formats with es-ES grouping and no decimals", () => {
    expect(formatNumber(1234567)).toBe("1.234.567");
    expect(formatNumber(0)).toBe("0");
  });
});

describe("colorFor", () => {
  it("is deterministic and returns a palette hex", () => {
    expect(colorFor("Spain")).toBe(colorFor("Spain"));
    expect(colorFor("Spain")).toMatch(/^#[0-9a-f]{6}$/i);
  });
});

describe("filterLabel", () => {
  it("maps known keys and falls back to the raw key", () => {
    expect(filterLabel("sex")).toBe("Sexo");
    expect(filterLabel("sex", "en")).toBe("Sex");
    expect(filterLabel("unknown_key")).toBe("unknown_key");
  });
});

describe("downloadCsv", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("builds a CSV with the union of columns and quoted cells", () => {
    const parts: string[] = [];
    vi.stubGlobal(
      "Blob",
      class {
        constructor(input: string[]) {
          parts.push(input.join(""));
        }
      },
    );
    vi.stubGlobal("URL", {
      createObjectURL: () => "blob:fake",
      revokeObjectURL: vi.fn(),
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    downloadCsv(
      [
        { country: "Spain", value: 10 },
        { country: 'Quote"d', value: 20 },
      ],
      "out.csv",
    );

    expect(parts).toHaveLength(1);
    const [header, ...rows] = parts[0].split("\n");
    expect(header).toBe("country,value");
    expect(rows[0]).toBe('"Spain","10"');
    expect(rows[1]).toBe('"Quote""d","20"');
  });

  it("does nothing for empty records", () => {
    const spy = vi.fn();
    vi.stubGlobal("URL", { createObjectURL: spy, revokeObjectURL: vi.fn() });
    downloadCsv([], "out.csv");
    expect(spy).not.toHaveBeenCalled();
  });
});
