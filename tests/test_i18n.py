"""Tests de la capa de localización de metadatos."""

from __future__ import annotations

import pytest

from open_data_hub.core.i18n import L, normalize_lang, resolve


def test_L_fills_missing_english_with_spanish() -> None:
    assert L("Hola") == {"es": "Hola", "en": "Hola"}
    assert L("Hola", "Hi") == {"es": "Hola", "en": "Hi"}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, "es"),
        ("", "es"),
        ("en", "en"),
        ("EN", "en"),
        ("en-US", "en"),
        ("es-ES,es;q=0.9", "es"),
        ("fr", "es"),  # no soportado -> default
    ],
)
def test_normalize_lang(raw: str | None, expected: str) -> None:
    assert normalize_lang(raw) == expected


def test_resolve_dict_and_fallbacks() -> None:
    value = {"es": "Criminalidad", "en": "Crime"}
    assert resolve(value, "en") == "Crime"
    assert resolve(value, "es") == "Criminalidad"
    # idioma ausente -> fallback al por defecto
    assert resolve({"es": "Solo ES"}, "en") == "Solo ES"
    # sin idioma por defecto -> primer valor
    assert resolve({"fr": "Bonjour"}, "en") == "Bonjour"


def test_resolve_plain_string_is_language_agnostic() -> None:
    assert resolve("INE", "en") == "INE"
    assert resolve("INE", "es") == "INE"
