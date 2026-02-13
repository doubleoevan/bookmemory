import { Toaster } from "@bookmemory/ui";
import { Outlet } from "react-router-dom";
import { Header } from "@/layouts/Header";
import { Footer } from "@/layouts/Footer";
import { useTheme } from "@/app/theme";

/** App layout */
export function AppShell() {
  const { theme } = useTheme();
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        <Outlet /> {/* routed page content */}
      </main>

      <Footer />
      <Toaster theme={theme} position="top-center" richColors={false} />
    </div>
  );
}
