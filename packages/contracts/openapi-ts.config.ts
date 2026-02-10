import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "./openapi/bookmemory.openapi.json",
  output: {
    path: "./src/gen",
    entryFile: false,
  },
  client: "fetch",
});
