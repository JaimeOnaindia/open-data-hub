"""Dimensión canónica de geografía: código de fuente → ISO 3166-1 alpha-2.

Primera dimensión conforme del futuro warehouse. Permite relacionar el mismo país
entre fuentes que lo nombran distinto. Empezamos por los códigos `geo` de Eurostat,
que son casi ISO salvo excepciones (EL→GR, UK→GB) y agregados supranacionales.

Datos de referencia que mantenemos nosotros (no se descargan). Un valor `None` marca
un agregado (no es un país) o un código sin mapear.
"""

from __future__ import annotations

# Eurostat geo code -> ISO 3166-1 alpha-2 (None = agregado / no país)
GEO_TO_ISO: dict[str, str | None] = {
    # UE-27
    "BE": "BE", "BG": "BG", "CZ": "CZ", "DK": "DK", "DE": "DE", "EE": "EE",
    "IE": "IE", "EL": "GR", "ES": "ES", "FR": "FR", "HR": "HR", "IT": "IT",
    "CY": "CY", "LV": "LV", "LT": "LT", "LU": "LU", "HU": "HU", "MT": "MT",
    "NL": "NL", "AT": "AT", "PL": "PL", "PT": "PT", "RO": "RO", "SI": "SI",
    "SK": "SK", "FI": "FI", "SE": "SE",
    # EFTA / Reino Unido
    "IS": "IS", "LI": "LI", "NO": "NO", "CH": "CH", "UK": "GB",
    # Candidatos / vecindad frecuentes en Eurostat
    "ME": "ME", "MK": "MK", "AL": "AL", "RS": "RS", "TR": "TR", "BA": "BA",
    "XK": "XK", "MD": "MD", "UA": "UA", "GE": "GE",
    # Terceros países habituales
    "US": "US", "JP": "JP",
    # Agregados supranacionales (no son países)
    "EU": None, "EU27_2020": None, "EU28": None, "EU27_2007": None,
    "EA": None, "EA12": None, "EA19": None, "EA20": None, "EA21": None,
    "EEA": None, "EEA31": None, "EEA30_2007": None, "EFTA": None,
}


def to_iso(geo_code: str | None) -> str | None:
    """ISO alpha-2 para un código `geo` de Eurostat, o `None` si es agregado/desconocido."""
    if not geo_code:
        return None
    return GEO_TO_ISO.get(geo_code.strip())


def is_country(geo_code: str | None) -> bool:
    return to_iso(geo_code) is not None
