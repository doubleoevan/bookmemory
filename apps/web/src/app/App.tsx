import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@/layouts/AppShell";
import { LoginPage } from "@/pages/LoginPage";
import { BookmarksHomePage } from "@/pages/BookmarksHomePage";
import { useCurrentUser } from "@/features/authentication/hooks/useCurrentUser";

export default function App() {
  const { user } = useCurrentUser();

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={user ? <BookmarksHomePage /> : <Navigate to="/login" replace />} />
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
