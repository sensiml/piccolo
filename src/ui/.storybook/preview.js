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

import { LightTheme } from "../src/components/Themes";

import i18n from "../src/i18n";
import { I18nextProvider } from "react-i18next";
import { addDecorator } from "@storybook/react";

addDecorator((storyFn) => <LightTheme>{storyFn()}</LightTheme>);
addDecorator((storyFn) => <I18nextProvider i18n={i18n}>{storyFn()}</I18nextProvider>);

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  i18n,
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
};
