from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field


class DatasetViewSummary(BaseModel):
    key: str
    label: str
    category_col: str
    category_label: str
    filter_cols: list[str] = Field(default_factory=list)


class DatasetTablePayload(BaseModel):
    view: DatasetViewSummary
    records: list[dict[str, Any]]


@dataclass(frozen=True)
class DatasetViewConfig:
    key: str
    label: str
    fetcher: Callable[..., pd.DataFrame]
    category_col: str
    category_label: str
    filter_cols: tuple[str, ...] = ()

    def summary(self) -> DatasetViewSummary:
        return DatasetViewSummary(
            key=self.key,
            label=self.label,
            category_col=self.category_col,
            category_label=self.category_label,
            filter_cols=list(self.filter_cols),
        )


DatasetViews = dict[str, DatasetViewConfig]
CountryDatasetViews = dict[str, DatasetViews]
