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

import i18n from "i18next";

import EnCommon from "./locales/en/common.json";
import EnAccount from "./locales/en/account.json";
import EnComponents from "./locales/en/componets.json";
import EnForms from "./locales/en/forms.json";
import EnLayout from "./locales/en/layout.json";
import EnNavigation from "./locales/en/navigation.json";
import EnModels from "./locales/en/models.json";
import EnProjects from "./locales/en/projects.json";
import EnDataManager from "./locales/en/data-manager.json";
import EnExploreModels from "./locales/en/explore-models.json";
import EnPipelines from "./locales/en/pipelines.json";
import EnQueries from "./locales/en/queries.json";
import EnTeam from "./locales/en/team.json";
import EnAuth from "./locales/en/auth.json";

const loadWithCommon = (loadedResource = {}) => {
  return { ...EnCommon, ...loadedResource };
};

i18n.init({
  resources: {
    en: {
      common: EnCommon,
      components: loadWithCommon(EnComponents),
      account: loadWithCommon(EnAccount),
      forms: EnForms,
      layout: loadWithCommon(EnLayout),
      navigation: EnNavigation,
      models: loadWithCommon(EnModels),
      auth: EnAuth,
      projects: loadWithCommon(EnProjects),
      "data-manager": loadWithCommon(EnDataManager),
      "explore-models": loadWithCommon(EnExploreModels),
      pipelines: loadWithCommon(EnPipelines),
      queries: loadWithCommon(EnQueries),
      team: loadWithCommon(EnTeam),
    },
  },

  fallbackLng: ["en"],
  debug: false,

  // have a common namespace used around the full app
  ns: [
    "common",
    "components",
    "account",
    "forms",
    "layout",
    "navigation",
    "models",
    "auth",
    "project",
    "data-manager",
    "pipelines",
  ],
  defaultNS: "common",

  interpolation: {
    escapeValue: false,
  },

  // in case loading from service like s3 backet
  react: {
    wait: true,
  },

  // keySeparator: false, // we use content as keys
});

export default i18n;
