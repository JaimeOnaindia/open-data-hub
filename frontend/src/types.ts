// Contrato de la API (espejo de los modelos pydantic en backend/src/open_data_hub/api.py).

export interface DatasetSummary {
  key: string;
  label: string;
  description: string;
  source_name: string;
}

export interface CountrySummary {
  code: string;
  name: string;
  flag: string;
  datasets: DatasetSummary[];
}

export interface DatasetIndexItem extends DatasetSummary {
  country_code: string;
  country_name: string;
  country_flag: string;
}

export interface DatasetViewSummary {
  key: string;
  label: string;
  category_col: string;
  category_label: string;
  filter_cols: string[];
}

/** Una observación tidy: dimensiones arbitrarias + year + value. */
export type DataRecord = Record<string, string | number | null>;

export interface DatasetTablePayload {
  view: DatasetViewSummary;
  records: DataRecord[];
}
