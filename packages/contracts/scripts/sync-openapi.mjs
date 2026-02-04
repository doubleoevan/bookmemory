import fs from "node:fs/promises";

// fetch openapi.json
const apiBaseUrl = process.env.API_BASE_URL ?? "http://localhost:8000";
const url = `${apiBaseUrl}/openapi.json`;
const response = await fetch(url, {
  headers: {
    accept: "application/json",
  },
});
if (!response.ok) {
  throw new Error(`Failed to fetch OpenAPI: ${response.status} ${response.statusText}`);
}

// write openapi.json to typescript contracts
const json = await response.json();
await fs.mkdir(new URL("../openapi", import.meta.url), { recursive: true });
await fs.writeFile(
  new URL("../openapi/bookmemory.openapi.json", import.meta.url),
  JSON.stringify(json, null, 2),
  "utf8",
);
console.log("Synced OpenAPI to packages/contracts/openapi/bookmemory.openapi.json");
