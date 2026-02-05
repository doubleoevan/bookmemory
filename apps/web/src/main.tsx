import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppProviders } from "@/providers/Providers";
import App from "@/app/App";
import "@/index.css";
import "@bookmemory/ui/styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>,
);
