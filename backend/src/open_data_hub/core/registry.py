from __future__ import annotations

from pydantic import BaseModel, Field


class DatasetConfig(BaseModel):
    key: str = Field(description="Slug interno, ej. 'crime'")
    label: str = Field(description="Etiqueta visible en la UI")
    description: str
    source_name: str = Field(description="Organismo oficial: INE, DGT, Eurostat, …")


class CountryConfig(BaseModel):
    code: str = Field(min_length=2, max_length=2, description="ISO 3166-1 alpha-2 en minúsculas")
    name: str
    flag: str = Field(description="Emoji de la bandera")
    datasets: list[DatasetConfig]

    def dataset(self, key: str) -> DatasetConfig:
        for ds in self.datasets:
            if ds.key == key:
                return ds
        raise KeyError(f"Dataset '{key}' no registrado para {self.code}")


COUNTRIES: dict[str, CountryConfig] = {
    "es": CountryConfig(
        code="es",
        name="España",
        flag="🇪🇸",
        datasets=[
            DatasetConfig(
                key="crime",
                label="Criminalidad",
                description=(
                    "Estadística de Condenados (adultos). Delitos por tipo, sexo y nacionalidad."
                ),
                source_name="INE",
            ),
            DatasetConfig(
                key="prices",
                label="Precios",
                description="Índice de Precios de Consumo nacional por grupos ECOICOP.",
                source_name="INE",
            ),
            DatasetConfig(
                key="labor",
                label="Mercado laboral",
                description="Tasas de paro por territorio, sexo y grupo de edad.",
                source_name="INE",
            ),
            DatasetConfig(
                key="demography",
                label="Demografía",
                description="Indicadores demográficos básicos y fenómenos demográficos.",
                source_name="INE",
            ),
        ],
    ),
}


def get_country(code: str) -> CountryConfig:
    try:
        return COUNTRIES[code.lower()]
    except KeyError as exc:
        raise KeyError(f"País '{code}' no registrado") from exc
