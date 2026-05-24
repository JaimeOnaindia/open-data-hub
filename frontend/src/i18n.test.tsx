import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it } from "vitest";

import { LangProvider, useLang, useT } from "./i18n";

function wrapper({ children }: { children: ReactNode }) {
  return <LangProvider>{children}</LangProvider>;
}

describe("i18n", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("defaults to Spanish and switches to English, persisting the choice", () => {
    const { result } = renderHook(() => ({ ctx: useLang(), t: useT() }), { wrapper });

    expect(result.current.ctx.lang).toBe("es");
    expect(result.current.t("dataset.view")).toBe("Vista");

    act(() => result.current.ctx.setLang("en"));

    expect(result.current.ctx.lang).toBe("en");
    expect(result.current.t("dataset.view")).toBe("View");
    expect(localStorage.getItem("odh.lang")).toBe("en");
  });

  it("reads the persisted language on init", () => {
    localStorage.setItem("odh.lang", "en");
    const { result } = renderHook(() => useT(), { wrapper });
    expect(result.current("catalog.title")).toBe("Open data catalogue");
  });
});
