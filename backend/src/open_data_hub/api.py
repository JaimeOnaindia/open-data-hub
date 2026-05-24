from __future__ import annotations

from functools import lru_cache
from typing import Any, cast

import pandas as pd
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from open_data_hub.core.datasets import (
    DatasetTablePayload,
    DatasetViewConfig,
    DatasetViews,
    DatasetViewSummary,
)
from open_data_hub.core.i18n import normalize_lang, resolve
from open_data_hub.core.storage import read_view
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
    version="1.0.0",
    description="API JSON para dashboards de datos públicos abiertos. Versión estable: /api/v1.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# --- Handlers (registrados en los routers más abajo) ------------------------


def health() -> dict[str, str]:
    return {"status": "ok"}


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


def list_dataset_views(
    country_code: str, dataset_key: str, lang: str = Query(default="es")
) -> list[DatasetViewSummary]:
    locale = normalize_lang(lang)
    return [
        view.summary(locale) for view in _get_dataset_views(country_code, dataset_key).values()
    ]


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


def list_crime_views(lang: str = Query(default="es")) -> list[CrimeViewSummary]:
    return list_dataset_views("es", "crime", lang)


def get_crime_view(
    view_key: str,
    nult: int = Query(default=10, ge=2, le=20),
    lang: str = Query(default="es"),
) -> CrimeTablePayload:
    return get_dataset_view("es", "crime", view_key, nult, lang)


# --- Routers ----------------------------------------------------------------
# /api/v1 es el contrato estable. /api (incl. /api/crime) queda como alias
# deprecado para no romper consumidores anteriores; se eliminará en una v2.

v1 = APIRouter(prefix="/api/v1", tags=["v1"])
v1.add_api_route("/health", health, methods=["GET"])
v1.add_api_route("/countries", list_countries, methods=["GET"])
v1.add_api_route("/datasets", list_datasets, methods=["GET"])
v1.add_api_route(
    "/datasets/{country_code}/{dataset_key}/views", list_dataset_views, methods=["GET"]
)
v1.add_api_route(
    "/datasets/{country_code}/{dataset_key}/views/{view_key}",
    get_dataset_view,
    methods=["GET"],
)

legacy = APIRouter(prefix="/api", tags=["deprecated"], deprecated=True)
legacy.add_api_route("/health", health, methods=["GET"])
legacy.add_api_route("/countries", list_countries, methods=["GET"])
legacy.add_api_route("/datasets", list_datasets, methods=["GET"])
legacy.add_api_route(
    "/datasets/{country_code}/{dataset_key}/views", list_dataset_views, methods=["GET"]
)
legacy.add_api_route(
    "/datasets/{country_code}/{dataset_key}/views/{view_key}",
    get_dataset_view,
    methods=["GET"],
)
legacy.add_api_route("/crime/views", list_crime_views, methods=["GET"])
legacy.add_api_route("/crime/views/{view_key}", get_crime_view, methods=["GET"])

app.include_router(v1)
app.include_router(legacy)


# --- Helpers internos -------------------------------------------------------


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
    """Sirve la vista desde el almacén persistido; si aún no se ha ingestado, en vivo."""
    df = read_view(country_code, dataset_key, view_key)
    if df is None:
        df = _get_dataset_view(country_code, dataset_key, view_key).fetcher(nult=nult)
    return _last_n_years(df, nult)


def _last_n_years(df: pd.DataFrame, nult: int) -> pd.DataFrame:
    """Recorta a los últimos `nult` años distintos (equivalente a `nult` sobre el almacén)."""
    if df.empty or "year" not in df.columns:
        return df
    years = sorted(int(y) for y in df["year"].dropna().unique())
    keep = set(years[-nult:])
    return df[df["year"].isin(keep)]


def _frame_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = cast(list[dict[str, Any]], df.to_dict(orient="records"))
    return [{key: _json_value(value) for key, value in record.items()} for record in records]


def _json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    return value
