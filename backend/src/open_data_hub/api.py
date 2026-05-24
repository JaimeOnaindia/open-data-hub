from __future__ import annotations

from functools import lru_cache
from typing import Any, cast

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from open_data_hub.core import COUNTRIES
from open_data_hub.core.datasets import (
    CountryDatasetViews,
    DatasetTablePayload,
    DatasetViewConfig,
    DatasetViews,
    DatasetViewSummary,
)
from open_data_hub.countries.es.sources.ine_datasets import ES_DATASET_VIEWS


class DatasetSummary(BaseModel):
    key: str
    label: str
    description: str
    source_name: str


class CountrySummary(BaseModel):
    code: str
    name: str
    flag: str
    datasets: list[DatasetSummary]


class DatasetIndexItem(DatasetSummary):
    country_code: str
    country_name: str
    country_flag: str


CrimeViewSummary = DatasetViewSummary
CrimeTablePayload = DatasetTablePayload


DATASET_VIEWS_BY_COUNTRY: dict[str, CountryDatasetViews] = {
    "es": ES_DATASET_VIEWS,
}


app = FastAPI(
    title="Open Data Hub API",
    version="0.1.0",
    description="API JSON para dashboards de datos públicos abiertos.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/countries")
def list_countries() -> list[CountrySummary]:
    return [
        CountrySummary(
            code=country.code,
            name=country.name,
            flag=country.flag,
            datasets=[
                DatasetSummary(
                    key=dataset.key,
                    label=dataset.label,
                    description=dataset.description,
                    source_name=dataset.source_name,
                )
                for dataset in country.datasets
            ],
        )
        for country in COUNTRIES.values()
    ]


@app.get("/api/datasets")
def list_datasets() -> list[DatasetIndexItem]:
    return [
        DatasetIndexItem(
            country_code=country.code,
            country_name=country.name,
            country_flag=country.flag,
            key=dataset.key,
            label=dataset.label,
            description=dataset.description,
            source_name=dataset.source_name,
        )
        for country in COUNTRIES.values()
        for dataset in country.datasets
    ]


@app.get("/api/datasets/{country_code}/{dataset_key}/views")
def list_dataset_views(country_code: str, dataset_key: str) -> list[DatasetViewSummary]:
    return [view.summary() for view in _get_dataset_views(country_code, dataset_key).values()]


@app.get("/api/datasets/{country_code}/{dataset_key}/views/{view_key}")
def get_dataset_view(
    country_code: str,
    dataset_key: str,
    view_key: str,
    nult: int = Query(default=10, ge=2, le=20),
) -> DatasetTablePayload:
    view = _get_dataset_view(country_code, dataset_key, view_key)
    records = _frame_to_records(_load_dataset_view(country_code, dataset_key, view.key, nult))
    return DatasetTablePayload(view=view.summary(), records=records)


@app.get("/api/crime/views")
def list_crime_views() -> list[CrimeViewSummary]:
    return list_dataset_views("es", "crime")


@app.get("/api/crime/views/{view_key}")
def get_crime_view(
    view_key: str,
    nult: int = Query(default=10, ge=2, le=20),
) -> CrimeTablePayload:
    return get_dataset_view("es", "crime", view_key, nult)


def _get_dataset_views(country_code: str, dataset_key: str) -> DatasetViews:
    country = COUNTRIES.get(country_code.lower())
    if country is None:
        raise HTTPException(status_code=404, detail=f"País no registrado: {country_code}")

    try:
        country.dataset(dataset_key)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset no registrado: {dataset_key}",
        ) from exc

    try:
        return DATASET_VIEWS_BY_COUNTRY[country.code][dataset_key]
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset sin vistas configuradas: {country.code}/{dataset_key}",
        ) from exc


def _get_dataset_view(
    country_code: str,
    dataset_key: str,
    view_key: str,
) -> DatasetViewConfig:
    try:
        return _get_dataset_views(country_code, dataset_key)[view_key]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Vista no registrada: {view_key}") from exc


@lru_cache(maxsize=64)
def _load_dataset_view(
    country_code: str,
    dataset_key: str,
    view_key: str,
    nult: int,
) -> pd.DataFrame:
    return _get_dataset_view(country_code, dataset_key, view_key).fetcher(nult=nult)


def _frame_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = cast(list[dict[str, Any]], df.to_dict(orient="records"))
    return [{key: _json_value(value) for key, value in record.items()} for record in records]


def _json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    return value
