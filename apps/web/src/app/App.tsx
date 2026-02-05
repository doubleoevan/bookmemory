import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@/app/AppShell";
import { Login } from "@/screen/Login";
import { useCurrentUser } from "@/auth/useCurrentUser";

export default function App() {
  const { user } = useCurrentUser();

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={user ? <div>Home</div> : <Navigate to="/login" replace />} />
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
