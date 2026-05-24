from __future__ import annotations

from pydantic import BaseModel, Field


class DatasetConfig(BaseModel):
    key: str = Field(description="Slug interno, ej. 'crime'")
    label: str = Field(description="Etiqueta visible en la UI")
    description: str
    source_name: str = Field(description="Organismo oficial: INE, DGT, Eurostat, …")


class CountryConfig(BaseModel):
    """Un proveedor de datos: instituto nacional (ES/INE) o fuente multilateral (EU/Eurostat).

    `code` admite ISO 3166-1 alpha-2, incluidas reservas excepcionales como `eu`.
    """

    code: str = Field(min_length=2, max_length=2, description="ISO 3166-1 alpha-2 en minúsculas")
    name: str
    flag: str = Field(description="Emoji de la bandera")
    datasets: list[DatasetConfig]

    def dataset(self, key: str) -> DatasetConfig:
        for ds in self.datasets:
            if ds.key == key:
                return ds
        raise KeyError(f"Dataset '{key}' no registrado para {self.code}")
