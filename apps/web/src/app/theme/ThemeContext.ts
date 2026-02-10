import { createContext } from "react";
import type { Theme } from "@/app/theme/themeStorage";
import { ThemeState } from "@/app/theme/ThemeProvider";

export type ThemeContextValue = ThemeState & {
  setTheme: (theme: Theme) => void;
};

export const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);
