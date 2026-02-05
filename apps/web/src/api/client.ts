const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function httpRequest(path: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  headers.set("accept", "application/json");

  const url = `${API_BASE_URL}${path}`;
  return fetch(url, {
    ...init,
    headers,
    credentials: "include",
  });
}

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await httpRequest(path, init);
  if (!response.ok) {
    throw response;
  }
  return (await response.json()) as T;
}
