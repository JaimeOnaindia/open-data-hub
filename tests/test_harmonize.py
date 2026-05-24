"""Tests de la dimensión canónica de geografía."""

from __future__ import annotations

from open_data_hub.harmonize.geo import is_country, to_iso


def test_to_iso_maps_eurostat_quirks() -> None:
    assert to_iso("ES") == "ES"
    assert to_iso("EL") == "GR"  # Grecia
    assert to_iso("UK") == "GB"  # Reino Unido


def test_to_iso_aggregates_and_unknown_are_none() -> None:
    assert to_iso("EU27_2020") is None
    assert to_iso("EA20") is None
    assert to_iso("ZZ") is None
    assert to_iso(None) is None
    assert to_iso("") is None


def test_is_country() -> None:
    assert is_country("FR") is True
    assert is_country("EU27_2020") is False
