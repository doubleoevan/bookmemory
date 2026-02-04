const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  // set the headers
  const headers = new Headers(init?.headers);
  headers.set("accept", "application/json");

  // return the response
  const url = `${API_BASE_URL}${path}`;
  return await fetch(url, {
    ...init,
    headers,
    credentials: "include",
  });
}
