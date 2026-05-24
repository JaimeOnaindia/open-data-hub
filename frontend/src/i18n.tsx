import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type Lang = "es" | "en";

const STORAGE_KEY = "odh.lang";

const es = {
  "app.subtitle": "Datos públicos abiertos · multi-país",
  "catalog.loading": "Cargando catálogo…",
  "catalog.title": "Catálogo de datos abiertos",
  "catalog.desc": "Datos en directo desde institutos oficiales, servidos por una API propia.",
  "dataset.loadingViews": "Cargando vistas…",
  "dataset.loadingData": "Cargando datos…",
  "dataset.subtitle": "Datos en directo desde la fuente oficial.",
  "dataset.titleFallback": "Cargando…",
  "dataset.view": "Vista",
  "dataset.years": "Años",
  "dataset.downloadCsv": "Descargar CSV",
  "dataset.trend": "Evolución temporal",
  "dataset.trendDesc": "Top 8 categorías por valor acumulado.",
  "dataset.empty": "No hay datos para estos filtros.",
  "metric.total": "Total registrado",
  "metric.years": "Años disponibles",
  "chart.year": "Año",
} as const;

export type TKey = keyof typeof es;

const en: Record<TKey, string> = {
  "app.subtitle": "Open public data · multi-country",
  "catalog.loading": "Loading catalogue…",
  "catalog.title": "Open data catalogue",
  "catalog.desc": "Live data from official statistics institutes, served by our own API.",
  "dataset.loadingViews": "Loading views…",
  "dataset.loadingData": "Loading data…",
  "dataset.subtitle": "Live data from the official source.",
  "dataset.titleFallback": "Loading…",
  "dataset.view": "View",
  "dataset.years": "Years",
  "dataset.downloadCsv": "Download CSV",
  "dataset.trend": "Time series",
  "dataset.trendDesc": "Top 8 categories by accumulated value.",
  "dataset.empty": "No data for these filters.",
  "metric.total": "Total recorded",
  "metric.years": "Years available",
  "chart.year": "Year",
};

const STRINGS: Record<Lang, Record<TKey, string>> = { es, en };

function readStoredLang(): Lang {
  const stored = typeof localStorage !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
  return stored === "en" || stored === "es" ? stored : "es";
}

interface LangContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
}

const LangContext = createContext<LangContextValue | null>(null);

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(readStoredLang);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = (next: Lang) => {
    localStorage.setItem(STORAGE_KEY, next);
    setLangState(next);
  };

  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>;
}

export function useLang(): LangContextValue {
  const ctx = useContext(LangContext);
  if (!ctx) {
    throw new Error("useLang debe usarse dentro de <LangProvider>");
  }
  return ctx;
}

export function useT(): (key: TKey) => string {
  const { lang } = useLang();
  return (key: TKey) => STRINGS[lang][key];
}
