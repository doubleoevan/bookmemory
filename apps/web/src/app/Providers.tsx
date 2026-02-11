import type { ReactNode } from "react";
import { BrowserRouter } from "react-router-dom";
import { RouteAnalytics } from "@/app/RouteAnalytics";
import { ThemeProvider } from "@/app/theme";
import { BookmarksProvider } from "@/features/bookmarks/providers/bookmark";

/** App context providers */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <BrowserRouter>
      <RouteAnalytics />
      <ThemeProvider>
        <BookmarksProvider>{children}</BookmarksProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
