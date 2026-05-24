// URL base de la API. Configurable en build (VITE_API_URL) o en runtime
// (window.OPEN_DATA_HUB_API_URL), con fallback a localhost para desarrollo.

declare global {
  interface Window {
    OPEN_DATA_HUB_API_URL?: string;
  }
}

const runtimeUrl =
  typeof window !== "undefined" ? window.OPEN_DATA_HUB_API_URL : undefined;
const buildUrl = import.meta.env.VITE_API_URL as string | undefined;

export const API_URL = runtimeUrl ?? buildUrl ?? "http://localhost:8000";
