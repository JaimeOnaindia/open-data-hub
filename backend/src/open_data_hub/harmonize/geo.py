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


# Conjunto canónico de códigos ISO 3166-1 alpha-2 oficialmente asignados (países/territorios).
# No incluye reservas (EU) ni rangos de usuario (XC, ZZ), así que sirve para distinguir países
# de agregados supranacionales en fuentes que mezclan ambos (p. ej. el Banco Mundial).
ISO2_COUNTRIES: frozenset[str] = frozenset(
    [
        "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT", "AU", "AW",
        "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN",
        "BO", "BQ", "BR", "BS", "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG",
        "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ",
        "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "EH", "ER", "ES", "ET", "FI",
        "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GG", "GH", "GI", "GL",
        "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR",
        "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM",
        "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA",
        "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME",
        "MF", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU",
        "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP",
        "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PR",
        "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB", "SC", "SD",
        "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SV",
        "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO",
        "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE",
        "VG", "VI", "VN", "VU", "WF", "WS", "YE", "YT", "ZA", "ZM", "ZW",
    ]
)


def is_iso2_country(code: str | None) -> bool:
    """True si `code` es un código de país ISO 3166-1 alpha-2 oficial (no agregado)."""
    return code is not None and code.strip().upper() in ISO2_COUNTRIES
