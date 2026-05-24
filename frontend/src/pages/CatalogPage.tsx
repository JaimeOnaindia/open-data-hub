import { Link } from "react-router-dom";

import { useCountries } from "../api/queries";

export function CatalogPage() {
  const { data: countries, isLoading, isError, error } = useCountries();

  if (isLoading) {
    return <div className="status">Cargando catálogo…</div>;
  }
  if (isError) {
    return <div className="error">{(error as Error).message}</div>;
  }

  return (
    <section className="content">
      <div className="topbar">
        <div>
          <h1>Catálogo de datos abiertos</h1>
          <p className="muted">
            Datos en directo desde institutos oficiales, servidos por una API propia.
          </p>
        </div>
      </div>

      <div className="catalog-grid">
        {(countries ?? []).map((country) =>
          country.datasets.map((dataset) => (
            <Link
              key={`${country.code}-${dataset.key}`}
              to={`/${country.code}/${dataset.key}`}
              className="catalog-card"
            >
              <span className="catalog-flag">{country.flag}</span>
              <strong>{dataset.label}</strong>
              <span className="muted">{country.name}</span>
              <p className="catalog-desc">{dataset.description}</p>
              <span className="catalog-source">{dataset.source_name}</span>
            </Link>
          )),
        )}
      </div>
    </section>
  );
}
