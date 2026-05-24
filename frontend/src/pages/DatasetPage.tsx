import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import { useDatasetView, useDatasetViews } from "../api/queries";
import { FilterSelect } from "../components/FilterSelect";
import { Metric } from "../components/Metric";
import { TrendChart } from "../components/TrendChart";
import { useLang, useT } from "../i18n";
import {
  buildChart,
  buildFilters,
  downloadCsv,
  formatNumber,
  type FilterValues,
} from "../lib/transform";

export function DatasetPage() {
  const t = useT();
  const { lang } = useLang();
  const { countryCode = "", datasetKey = "" } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();

  const viewsQuery = useDatasetViews(countryCode, datasetKey);
  const views = useMemo(() => viewsQuery.data ?? [], [viewsQuery.data]);

  const urlView = searchParams.get("view") ?? undefined;
  const years = Number(searchParams.get("years") ?? 10);
  const viewKey = urlView && views.some((v) => v.key === urlView) ? urlView : views[0]?.key;

  const viewQuery = useDatasetView(countryCode, datasetKey, viewKey, years);
  const payload = viewQuery.data;

  const filters = useMemo(() => buildFilters(payload, lang), [payload, lang]);
  const [filterValues, setFilterValues] = useState<FilterValues>({});
  useEffect(() => {
    setFilterValues(Object.fromEntries(filters.map((filter) => [filter.key, filter.defaults])));
  }, [filters]);

  const chart = useMemo(() => buildChart(payload, filterValues), [payload, filterValues]);
  const latestYear = chart.years.at(-1);
  const totalLatest = chart.data.find((d) => d.year === latestYear);
  const latestSum = totalLatest
    ? chart.categories.reduce((sum, category) => sum + (totalLatest[category] ?? 0), 0)
    : 0;

  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    next.set(key, value);
    setSearchParams(next, { replace: true });
  };

  if (viewsQuery.isLoading) {
    return (
      <section className="content">
        <div className="status">{t("dataset.loadingViews")}</div>
      </section>
    );
  }
  if (viewsQuery.isError) {
    return (
      <section className="content">
        <div className="error">{(viewsQuery.error as Error).message}</div>
      </section>
    );
  }

  return (
    <section className="content">
      <div className="topbar">
        <div>
          <h1>{payload?.view.label ?? t("dataset.titleFallback")}</h1>
          <p className="muted">{t("dataset.subtitle")}</p>
        </div>
      </div>

      <div className="toolbar">
        <label>
          {t("dataset.view")}
          <select
            value={viewKey ?? ""}
            onChange={(event) => updateParam("view", event.target.value)}
          >
            {views.map((view) => (
              <option key={view.key} value={view.key}>
                {view.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          {t("dataset.years")}: {years}
          <input
            type="range"
            min={2}
            max={20}
            value={years}
            onChange={(event) => updateParam("years", event.target.value)}
          />
        </label>

        <div className="filters">
          {filters.map((filter) => (
            <FilterSelect
              key={filter.key}
              filter={filter}
              value={filterValues[filter.key] ?? []}
              onChange={(value) =>
                setFilterValues((current) => ({ ...current, [filter.key]: value }))
              }
            />
          ))}
        </div>

        <button
          className="button"
          type="button"
          disabled={chart.records.length === 0}
          onClick={() => downloadCsv(chart.records, `${countryCode}_${datasetKey}_${viewKey}.csv`)}
        >
          {t("dataset.downloadCsv")}
        </button>
      </div>

      {viewQuery.isLoading ? <div className="status">{t("dataset.loadingData")}</div> : null}
      {viewQuery.isError ? (
        <div className="error">{(viewQuery.error as Error).message}</div>
      ) : null}

      {payload ? (
        <>
          <section className="metrics">
            <Metric
              label={`${t("metric.total")} (${latestYear ?? "-"})`}
              value={formatNumber(latestSum)}
            />
            <Metric label={t("metric.years")} value={chart.years.length} />
            <Metric label={payload.view.category_label} value={chart.categoryCount} />
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <strong>{t("dataset.trend")}</strong>
                <p className="muted">{t("dataset.trendDesc")}</p>
              </div>
            </div>
            {chart.data.length > 0 ? (
              <TrendChart chart={chart} />
            ) : (
              <div className="empty-state">{t("dataset.empty")}</div>
            )}
          </section>
        </>
      ) : null}
    </section>
  );
}
