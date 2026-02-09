/// <reference types="vite/client" />

declare type GtagArgs = [
  command: "js" | "config" | "event",
  target?: string | Date,
  params?: Record<string, unknown>,
];

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag: (...args: GtagArgs) => void;
  }
}

export {};
