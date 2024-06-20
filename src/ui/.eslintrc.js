/*
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
*/

module.exports = {
  settings: {
    "import/resolver": {
      node: {
        paths: ["./src"],
      },
    },
  },
  env: {
    browser: true,
    es2021: true,
    jest: true,
  },
  extends: [
    "plugin:react/recommended",
    "plugin:import/recommended",
    "plugin:prettier/recommended",
    "airbnb",
  ],
  parser: "babel-eslint",
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 7,
    sourceType: "module",
  },
  plugins: ["react", "prettier", "import"],
  overrides: [
    {
      files: ["*.spec.js", "*.test.js"],

      rules: {
        "jest/valid-expect": 0,
      },
    },
  ],
  rules: {
    "prettier/prettier": ["error"],
    "react/prop-types": "off",
    "prefer-arrow-callback": "off",

    "import/no-named-as-default": "off",
    "implicit-arrow-linebreak": "off",
    "import/no-extraneous-dependencie": "off",
    "import/prefer-default-export": "off",
    "import/no-named-as-default-member": "off",
    "import/order": "off",
    camelcase: "off",

    // logic
    "no-nested-ternary": "off",
    "no-underscore-dangle": "off",
    "no-restricted-globals": "off",
    // oop
    "class-methods-use-this": "off",
    // operators
    "operator-assignment": "off",
    "no-continue": "off",
    "no-plusplus": "off",
    "function-paren-newline": "off",

    // react
    "import/no-unresolved": "off",
    "react/jsx-curly-newline": "off",
    "react/jsx-indent": "off",
    "react/jsx-first-prop-new-line": [2, "multiline"],
    "react/jsx-max-props-per-line": [2, { maximum: 1, when: "multiline" }],
    "react/jsx-indent-props": [2, 2],
    "react/jsx-closing-bracket-location": [2, "tag-aligned"],
    "react/jsx-no-unused-expressions": "off",
    "react/forbid-prop-types": "off",
    "react/destructuring-assignment": "off",
    "react/jsx-filename-extension": "off",
    "react/jsx-curly-brace-presence": "off",
    "react/no-array-index-key": "off",
    "react/jsx-props-no-spreading": "off",
    "react/jsx-one-expression-per-line": "off",
    "react/jsx-boolean-value": "off",
    "react/jsx-wrap-multilines": ["error", { arrow: true, return: true, declaration: false }],
    "react/no-unknown-property": [
      2,
      { ignore: ["x", "y", "d", "fill", "points", "key", "variant"] },
    ],

    "no-console": process.env.NODE_ENV === "development" ? "off" : "error",

    "max-len": ["error", { code: 100 }],
    quotes: [2, "double", { allowTemplateLiterals: true }],
    "comma-dangle": [
      "off",
      {
        arrays: "never",
        objects: "always",
        imports: "always",
        exports: "always",
        functions: "always",
      },
    ],
    indent: [
      "off",
      2,
      { offsetTernaryExpressions: false, SwitchCase: 1, ignoreComments: true, MemberExpression: 0 },
    ],
    // braking
    "arrow-body-style": "off",
    //  { overrides: { "?": "before", ":": "before" }}
    "operator-linebreak": ["error", "after", { overrides: { "?": "before", ":": "before" } }],
    "object-curly-newline": [
      "error",
      {
        ObjectExpression: { consistent: true, multiline: true },
        ObjectPattern: { consistent: true, multiline: true },
        ImportDeclaration: { consistent: true, multiline: true },
        ExportDeclaration: { consistent: true, multiline: true },
      },
    ],
    "no-unused-vars": ["error", { argsIgnorePattern: "^_" }], // ignore for _ name
    "no-param-reassign": [
      "error",
      {
        props: true,
        ignorePropertyModificationsForRegex: ["acc", "Acc"], // reduce
        ignorePropertyModificationsFor: ["acc", "accParams", "hiddenAcc", "Acc"], // reduce
      },
    ],
    "jsx-a11y/anchor-is-valid": "off",
  },
};
