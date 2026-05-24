from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from open_data_hub.core.i18n import Localizable, resolve


class DatasetViewSummary(BaseModel):
    key: str
    label: str
    category_col: str
    category_label: str
    filter_cols: list[str] = Field(default_factory=list)


class DatasetTablePayload(BaseModel):
    view: DatasetViewSummary
    records: list[dict[str, Any]]
    fetched_at: str | None = Field(
        default=None,
        description="ISO 8601 del snapshot servido; null si se sirvió en vivo.",
    )


@dataclass(frozen=True)
class DatasetViewConfig:
    key: str
    label: Localizable
    fetcher: Callable[..., pd.DataFrame]
    category_col: str
    category_label: Localizable
    filter_cols: tuple[str, ...] = ()

    def summary(self, lang: str) -> DatasetViewSummary:
        return DatasetViewSummary(
            key=self.key,
            label=resolve(self.label, lang),
            category_col=self.category_col,
            category_label=resolve(self.category_label, lang),
            filter_cols=list(self.filter_cols),
        )


DatasetViews = dict[str, DatasetViewConfig]
CountryDatasetViews = dict[str, DatasetViews]
