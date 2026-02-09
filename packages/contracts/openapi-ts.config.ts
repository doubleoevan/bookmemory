import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "./openapi/bookmemory.openapi.json",
  output: "./src",
  client: "fetch",
});
