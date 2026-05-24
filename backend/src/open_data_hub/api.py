from __future__ import annotations

from functools import lru_cache
from typing import Any, cast

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from open_data_hub.core.datasets import (
    DatasetTablePayload,
    DatasetViewConfig,
    DatasetViews,
    DatasetViewSummary,
)
from open_data_hub.core.i18n import normalize_lang, resolve
from open_data_hub.countries.catalog import COUNTRIES, DATASET_VIEWS_BY_COUNTRY


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
def list_countries(lang: str = Query(default="es")) -> list[CountrySummary]:
    locale = normalize_lang(lang)
    return [
        CountrySummary(
            code=country.code,
            name=resolve(country.name, locale),
            flag=country.flag,
            datasets=[
                DatasetSummary(
                    key=dataset.key,
                    label=resolve(dataset.label, locale),
                    description=resolve(dataset.description, locale),
                    source_name=dataset.source_name,
                )
                for dataset in country.datasets
            ],
        )
        for country in COUNTRIES.values()
    ]


@app.get("/api/datasets")
def list_datasets(lang: str = Query(default="es")) -> list[DatasetIndexItem]:
    locale = normalize_lang(lang)
    return [
        DatasetIndexItem(
            country_code=country.code,
            country_name=resolve(country.name, locale),
            country_flag=country.flag,
            key=dataset.key,
            label=resolve(dataset.label, locale),
            description=resolve(dataset.description, locale),
            source_name=dataset.source_name,
        )
        for country in COUNTRIES.values()
        for dataset in country.datasets
    ]


@app.get("/api/datasets/{country_code}/{dataset_key}/views")
def list_dataset_views(
    country_code: str, dataset_key: str, lang: str = Query(default="es")
) -> list[DatasetViewSummary]:
    locale = normalize_lang(lang)
    return [
        view.summary(locale) for view in _get_dataset_views(country_code, dataset_key).values()
    ]


@app.get("/api/datasets/{country_code}/{dataset_key}/views/{view_key}")
def get_dataset_view(
    country_code: str,
    dataset_key: str,
    view_key: str,
    nult: int = Query(default=10, ge=2, le=20),
    lang: str = Query(default="es"),
) -> DatasetTablePayload:
    view = _get_dataset_view(country_code, dataset_key, view_key)
    records = _frame_to_records(_load_dataset_view(country_code, dataset_key, view.key, nult))
    return DatasetTablePayload(view=view.summary(normalize_lang(lang)), records=records)


@app.get("/api/crime/views")
def list_crime_views(lang: str = Query(default="es")) -> list[CrimeViewSummary]:
    return list_dataset_views("es", "crime", lang)


@app.get("/api/crime/views/{view_key}")
def get_crime_view(
    view_key: str,
    nult: int = Query(default=10, ge=2, le=20),
    lang: str = Query(default="es"),
) -> CrimeTablePayload:
    return get_dataset_view("es", "crime", view_key, nult, lang)


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
