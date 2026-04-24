import "@testing-library/jest-dom";

// jsdom does not implement ResizeObserver; stub it so canvas components
// that listen for container-size changes render in tests.
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
}
