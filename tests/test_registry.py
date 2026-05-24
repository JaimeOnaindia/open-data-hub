"""Invariantes del registro: cada país declarado tiene views, cada view es válida."""

from __future__ import annotations

from open_data_hub.api import DATASET_VIEWS_BY_COUNTRY
from open_data_hub.core.registry import COUNTRIES


def test_every_country_has_views_registered() -> None:
    for code, country in COUNTRIES.items():
        assert code in DATASET_VIEWS_BY_COUNTRY, f"País '{code}' sin views registradas"
        for ds in country.datasets:
            views = DATASET_VIEWS_BY_COUNTRY[code]
            assert ds.key in views, f"Dataset '{code}/{ds.key}' declarado sin views"


def test_views_keys_match_their_config() -> None:
    for _, datasets in DATASET_VIEWS_BY_COUNTRY.items():
        for _, views in datasets.items():
            for view_key, config in views.items():
                assert config.key == view_key, (
                    f"Inconsistencia: clave dict '{view_key}' != config.key '{config.key}'"
                )


def test_country_codes_are_iso_alpha2_lowercase() -> None:
    for code in COUNTRIES:
        assert len(code) == 2, f"Código '{code}' no es ISO alpha-2"
        assert code.islower(), f"Código '{code}' debe estar en minúsculas"


def test_dataset_view_filter_cols_are_strings() -> None:
    for _, datasets in DATASET_VIEWS_BY_COUNTRY.items():
        for _, views in datasets.items():
            for _, config in views.items():
                assert isinstance(config.filter_cols, tuple)
                for col in config.filter_cols:
                    assert isinstance(col, str) and col
