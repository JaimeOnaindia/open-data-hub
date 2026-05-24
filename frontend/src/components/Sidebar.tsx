import { NavLink } from "react-router-dom";

import { useLang, useT, type Lang } from "../i18n";
import type { CountrySummary } from "../types";

interface SidebarProps {
  countries: CountrySummary[];
}

const LANGS: Lang[] = ["es", "en"];

function LanguageToggle() {
  const { lang, setLang } = useLang();
  return (
    <div className="lang-toggle" role="group" aria-label="Idioma / Language">
      {LANGS.map((option) => (
        <button
          key={option}
          type="button"
          className={option === lang ? "active" : ""}
          aria-pressed={option === lang}
          onClick={() => setLang(option)}
        >
          {option.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

export function Sidebar({ countries }: SidebarProps) {
  const t = useT();
  return (
    <aside className="sidebar">
      <NavLink to="/" className="brand">
        <span className="brand-mark">OD</span>
        <span>Open Data Hub</span>
      </NavLink>
      <p className="muted">{t("app.subtitle")}</p>

      <LanguageToggle />

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
