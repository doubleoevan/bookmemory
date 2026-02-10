import type { ReactNode } from "react";
import { BrowserRouter } from "react-router-dom";
import { RouteAnalytics } from "@/app/RouteAnalytics";
import { ThemeProvider } from "@/app/theme";

/** App context providers */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <BrowserRouter>
      <RouteAnalytics />
      <ThemeProvider>{children}</ThemeProvider>
    </BrowserRouter>
  );
}
