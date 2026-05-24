import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, fetchJson } from "./client";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchJson", () => {
  it("returns parsed JSON on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ hello: "world" }),
      }),
    );
    const data = await fetchJson<{ hello: string }>("/api/x");
    expect(data).toEqual({ hello: "world" });
  });

  it("throws ApiError with the status on a non-ok response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 404, json: () => Promise.resolve({}) }),
    );
    await expect(fetchJson("/api/missing")).rejects.toBeInstanceOf(ApiError);
    await expect(fetchJson("/api/missing")).rejects.toMatchObject({ status: 404 });
  });
});
