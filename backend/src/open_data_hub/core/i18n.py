"""Localización ligera de metadatos (no de los datos en sí).

Un texto localizable es un `dict[str, str]` (`{"es": "...", "en": "..."}`) o un `str`
plano (mismo texto en todos los idiomas). `resolve` cae al idioma por defecto y luego
al primer valor disponible, así que un proveedor puede aportar solo un idioma.
"""

from __future__ import annotations

LocalizedStr = dict[str, str]
Localizable = LocalizedStr | str

DEFAULT_LANG = "es"
SUPPORTED_LANGS: tuple[str, ...] = ("es", "en")


def L(es: str, en: str | None = None) -> LocalizedStr:
    """Construye un texto localizable. Si falta `en`, reutiliza `es`."""
    return {"es": es, "en": en if en is not None else es}


def normalize_lang(lang: str | None) -> str:
    """Normaliza `?lang=` o un header Accept-Language a un idioma soportado."""
    if not lang:
        return DEFAULT_LANG
    code = lang.split(",")[0].split("-")[0].strip().lower()
    return code if code in SUPPORTED_LANGS else DEFAULT_LANG


def resolve(value: Localizable, lang: str) -> str:
    """Devuelve el texto en `lang`, con fallback al idioma por defecto y al primero."""
    if isinstance(value, str):
        return value
    return value.get(lang) or value.get(DEFAULT_LANG) or next(iter(value.values()), "")
