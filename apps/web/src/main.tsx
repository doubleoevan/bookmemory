import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppProviders } from "@/providers/Providers";
import App from "@/App";
import { enableMocks } from "@/mocks";
import "@/index.css";
import "@bookmemory/ui/styles.css";

// enable mock service worker in dev
if (import.meta.env.DEV) {
  await enableMocks();
}

// bootstrap Google Analytics in prod
const GA_ID = import.meta.env.VITE_GA_ID;
if (GA_ID && import.meta.env.PROD) {
  const scriptSrc = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  const existingScript = document.querySelector<HTMLScriptElement>(`script[src="${scriptSrc}"]`);
  if (!existingScript) {
    const script = document.createElement("script");
    script.async = true;
    script.src = scriptSrc;
    document.head.appendChild(script);
  }

  window.dataLayer = window.dataLayer || [];
  window.gtag =
    window.gtag ||
    function gtag() {
      // eslint-disable-next-line prefer-rest-params
      window?.dataLayer?.push?.(arguments);
    };

  window.gtag("js", new Date());
  window.gtag("config", GA_ID, { send_page_view: false });
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>,
);
