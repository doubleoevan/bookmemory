import { setupWorker } from "msw/browser";
import { handlers } from "@/mocks/handlers";

export const worker = setupWorker(...handlers);

worker.start({
  onUnhandledRequest(request) {
    // only mock our own API in dev
    const url = new URL(request.url);
    if (!url.pathname.startsWith("/api/")) {
      return;
    }
    console.warn("[MSW] Unhandled request:", request.method, url.pathname);
  },
});
