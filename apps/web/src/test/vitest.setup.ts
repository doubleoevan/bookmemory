import { Storage } from "happy-dom";
import { afterEach, beforeEach, vi } from "vitest";

// mock local storage and session storage
globalThis.localStorage = new Storage();
globalThis.sessionStorage = new Storage();
if (typeof window !== "undefined") {
  Object.defineProperty(window, "localStorage", {
    value: globalThis.localStorage,
    configurable: true,
  });
  Object.defineProperty(window, "sessionStorage", {
    value: globalThis.sessionStorage,
    configurable: true,
  });
}

beforeEach(() => {
  // clear storage before tests
  localStorage.clear();
  sessionStorage.clear();
});

afterEach(() => {
  // restore test mocks
  vi.restoreAllMocks();
});
