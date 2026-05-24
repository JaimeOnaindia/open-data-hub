import { useQuery } from "@tanstack/react-query";

import type {
  CountrySummary,
  DatasetTablePayload,
  DatasetViewSummary,
} from "../types";
import { fetchJson } from "./client";

export function useCountries() {
  return useQuery({
    queryKey: ["countries"],
    queryFn: ({ signal }) => fetchJson<CountrySummary[]>("/api/countries", signal),
    staleTime: 60 * 60 * 1000,
  });
}

export function useDatasetViews(countryCode: string, datasetKey: string) {
  return useQuery({
    queryKey: ["views", countryCode, datasetKey],
    queryFn: ({ signal }) =>
      fetchJson<DatasetViewSummary[]>(
        `/api/datasets/${countryCode}/${datasetKey}/views`,
        signal,
      ),
    staleTime: 60 * 60 * 1000,
  });
}

export function useDatasetView(
  countryCode: string,
  datasetKey: string,
  viewKey: string | undefined,
  nult: number,
) {
  return useQuery({
    queryKey: ["view", countryCode, datasetKey, viewKey, nult],
    queryFn: ({ signal }) =>
      fetchJson<DatasetTablePayload>(
        `/api/datasets/${countryCode}/${datasetKey}/views/${viewKey}?nult=${nult}`,
        signal,
      ),
    enabled: Boolean(viewKey),
    staleTime: 60 * 60 * 1000,
  });
}
