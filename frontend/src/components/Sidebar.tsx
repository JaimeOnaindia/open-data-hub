import { NavLink } from "react-router-dom";

import type { CountrySummary } from "../types";

interface SidebarProps {
  countries: CountrySummary[];
}

export function Sidebar({ countries }: SidebarProps) {
  return (
    <aside className="sidebar">
      <NavLink to="/" className="brand">
        <span className="brand-mark">OD</span>
        <span>Open Data Hub</span>
      </NavLink>
      <p className="muted">Datos públicos abiertos · multi-país</p>

      <nav className="nav">
        {countries.map((country) => (
          <div key={country.code} className="nav-country">
            <span className="nav-country-name">
              {country.flag} {country.name}
            </span>
            {country.datasets.map((dataset) => (
              <NavLink
                key={dataset.key}
                to={`/${country.code}/${dataset.key}`}
                className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              >
                {dataset.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  );
}
