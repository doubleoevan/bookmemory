import js from "@eslint/js";
import tseslint from "typescript-eslint";
import globals from "globals";

export default [
  js.configs.recommended,

  // TypeScript (non-type-aware) for all TS/TSX in this package
  ...tseslint.config({
    files: ["**/*.ts", "**/*.tsx"],
    extends: [...tseslint.configs.strict],
    languageOptions: {
      globals: {
        ...globals.es2022,
        ...globals.browser,
        ...globals.node,
      },
    },
  }),

  {
    ignores: ["dist/**"],
  },
];
