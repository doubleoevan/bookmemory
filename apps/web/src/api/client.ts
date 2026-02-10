import { client } from "@bookmemory/contracts";

// initializes the contract-aware api client on app startup
export function enableApi(): void {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  client.setConfig({
    baseUrl: API_BASE_URL,
    credentials: "include",
    headers: { accept: "application/json" },
    responseStyle: "data",
    throwOnError: true,
  });
}

// returns the typesafe result of an endpoint function from the api contract
export async function apiRequest<T>(
  // eslint-disable-next-line
  endpoint: (options?: any) => Promise<any>,
  // eslint-disable-next-line
  options?: any,
): Promise<T> {
  return await endpoint({
    responseStyle: "data",
    throwOnError: true,
    ...(options ?? {}),
  });
}
