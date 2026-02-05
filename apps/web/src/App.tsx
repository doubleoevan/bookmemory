import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@/layouts/AppShell";
import { Login } from "@/screen/Login";
import { BookmarkHome } from "@/screen/BookmarkHome";
import { useCurrentUser } from "@/features/logins/hooks/useCurrentUser";

export default function App() {
  const { user } = useCurrentUser();

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={user ? <BookmarkHome /> : <Navigate to="/login" replace />} />
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
