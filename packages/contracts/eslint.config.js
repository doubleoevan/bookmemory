import js from "@eslint/js";
import tseslint from "typescript-eslint";

import globals from "globals";

export default [
  // base JS rules for everything
  js.configs.recommended,

  // type-aware rules for TypeScript files only
  ...tseslint.config({
    files: ["src/**/*.ts", "src/**/*.tsx"],
    extends: [...tseslint.configs.strictTypeChecked],
    languageOptions: {
      parserOptions: {
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  }),

  // non-type-aware rules TypeScript files outside the src directory
  ...tseslint.config({
    files: ["**/*.ts", "**/*.tsx"],
    extends: [...tseslint.configs.strict],
  }),

  // node scripts like sync-openapi
  {
    files: ["scripts/**/*.mjs", "scripts/**/*.js"],
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.es2022,
        fetch: "readonly",
      },
    },
  },

  // ignore build and generated output
  {
    ignores: ["dist/**", "openapi/**", "**/*.gen.ts"],
  },
];
