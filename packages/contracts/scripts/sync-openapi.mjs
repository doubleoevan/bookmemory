import fs from "node:fs/promises";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

const OPENAPI_FILE = "bookmemory.openapi.json";
const OPENAPI_URL = new URL("../openapi/", import.meta.url);
const OPENAPI_FILE_URL = new URL(OPENAPI_FILE, OPENAPI_URL);

// fetch openapi.json
const response = await fetch(`${API_BASE_URL}/openapi.json`, {
  headers: { accept: "application/json" },
});
if (!response.ok) {
  throw new Error(`Failed to fetch OpenAPI: ${response.status} ${response.statusText}`);
}

// write openapi.json to the contracts directory
const json = await response.json();
await fs.mkdir(OPENAPI_URL, { recursive: true });
await fs.writeFile(OPENAPI_FILE_URL, JSON.stringify(json, null, 2), "utf8");
console.log(`Synced OpenAPI to packages/contracts/openapi/${OPENAPI_FILE}`);
