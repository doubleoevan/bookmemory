import { useContext } from "react";
import { type ThemeContextValue } from "@/app/theme/index";
import { ThemeContext } from "@/app/theme/ThemeContext";

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within <ThemeProvider />");
  }
  return context;
}
