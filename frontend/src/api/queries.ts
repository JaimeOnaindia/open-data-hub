import { useQuery } from "@tanstack/react-query";

import { useLang } from "../i18n";
import type {
  CountrySummary,
  DatasetTablePayload,
  DatasetViewSummary,
} from "../types";
import { fetchJson } from "./client";

const STALE = 60 * 60 * 1000;

export function useCountries() {
  const { lang } = useLang();
  return useQuery({
    queryKey: ["countries", lang],
    queryFn: ({ signal }) => fetchJson<CountrySummary[]>(`/api/countries?lang=${lang}`, signal),
    staleTime: STALE,
  });
}

export function useDatasetViews(countryCode: string, datasetKey: string) {
  const { lang } = useLang();
  return useQuery({
    queryKey: ["views", countryCode, datasetKey, lang],
    queryFn: ({ signal }) =>
      fetchJson<DatasetViewSummary[]>(
        `/api/datasets/${countryCode}/${datasetKey}/views?lang=${lang}`,
        signal,
      ),
    staleTime: STALE,
  });
}

export function useDatasetView(
  countryCode: string,
  datasetKey: string,
  viewKey: string | undefined,
  nult: number,
) {
  const { lang } = useLang();
  return useQuery({
    queryKey: ["view", countryCode, datasetKey, viewKey, nult, lang],
    queryFn: ({ signal }) =>
      fetchJson<DatasetTablePayload>(
        `/api/datasets/${countryCode}/${datasetKey}/views/${viewKey}?nult=${nult}&lang=${lang}`,
        signal,
      ),
    enabled: Boolean(viewKey),
    staleTime: STALE,
  });
}
