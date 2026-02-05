import { Outlet } from "react-router-dom";
import { Header } from "@/layouts/Header";
import { Footer } from "@/layouts/Footer";

/** App layout */
export function AppShell() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        <Outlet /> {/* routed page content */}
      </main>

      <Footer />
    </div>
  );
}
