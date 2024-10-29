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

export { getFirstPathPart, getCutLastPathPart } from "./utils";

export const ROUTES = {
  AUTH: {
    path: "/auth/",
    child: {
      LOGIN: {
        path: "/auth/login/",
        fullPath: "/auth/login/",
        name: "login",
        successRedirect: "home",
      },
      OAUTH_CALLBACK: {
        path: "/auth/oauth-callback/",
        fullPath: "/auth/oauth-callback/",
        name: "oauth-callback",
        successRedirect: "home",
      },
    },
  },
  ACCOUNT_SETTINGS: {
    path: "/account-settings/",
    name: "account-settings",
    child: {
      ACCOUNT_INFO: {
        path: "/account-settings/account-info/",
        name: "account-info",
      },
      ACCOUNT_SUBCRIPTIONS: {
        path: "/account-settings/account-subscriptions/",
        name: "account-subscription",
      },
      ACCOUNT_API_KEYS: {
        path: "/account-settings/account-api-keys/",
        name: "account-api-keys",
      },
    },
  },
  GET_STARTED: {
    path: {
      // eslint-disable-next-line max-len
      pathname: `${process.env.REACT_APP_MKT_URL}documentation/guides/getting-started/overview.html`,
    },
    name: "get-started",
  },
  DEMO: {
    path: "/demo/",
    name: "demo",
  },
  DOCUMENTATION: {
    path: {
      pathname: `${process.env.REACT_APP_MKT_URL}documentation`,
    },
    name: "documentation",
  },
  SUPPORT: {
    path: { pathname: `${process.env.REACT_APP_MKT_URL}support` },
    name: "support",
  },
  MAIN: {
    path: "/",
    HOME: {
      path: "/",
      name: "home",
    },
    PROJECT_SUMMARY: {
      path: "/summary/:projectUUID?/",
      name: "summary",
    },
    DATA_MANAGER: {
      path: "/data-manager/:projectUUID?/",
      name: "data-manager",
      child: {
        CAPTURES_SCREEN: {
          path: "/data-manager/:projectUUID?/captures/",
          name: "data-manager-captures",
        },
        CAPTURE_DETAILS_SCREEN: {
          path: "/data-manager/:projectUUID?/capture/:captureUUID?/",
          name: "data-manager-capture-details",
        },
      },
    },
    DATA_EXPLORER: {
      path: "/data-explorer/:projectUUID?/",
      name: "data-explorer",
      child: {
        QUERY_SCREEN: {
          path: "/data-explorer/:projectUUID?/queries/",
          name: "data-explorer-queries",
        },
        QUERY_DETAILS_SCREEN: {
          path: "/data-explorer/:projectUUID?/query/:queryUUID?/",
          name: "data-explorer-queries-details",
        },
        QUERY_CREATE_SCREEN: {
          path: "/data-explorer/:projectUUID?/query-create/",
          name: "data-explorer-queries-create",
        },
      },
    },
    MODEL_BUILD: {
      path: "/model-build/:projectUUID?/",
      name: "model-build",
      child: {
        SELECT_SCREEN: {
          path: "/model-build/:projectUUID?/select/",
          name: "select-screen",
        },
        FEATURE_EXTRACTOR: {
          path: "/model-build/:projectUUID?/feature-extractor/:pipelineUUID?/",
          name: "feature-extractor",
        },
        AUTOML: {
          path: "/model-build/:projectUUID?/automl-builder/:pipelineUUID?/",
          name: "automl-builder-screen",
        },
        CUSTOM: {
          path: "/model-build/:projectUUID?/custom-builder/:pipelineUUID?/",
          name: "custom-builder-screen",
        },
      },
    },
    MODEL_EXPLORE: {
      path: "/model-explore/:projectUUID?/:modelUUID?/",
      name: "model-explore",
      child: {
        CONFUSION_MATRIX: {
          path: "/model-explore/:projectUUID?/:modelUUID?/confusion-matrix/",
          name: "confusion-matrix",
        },
        FEATURE_VISUALIZATION: {
          path: "/model-explore/:projectUUID?/:modelUUID?/feature-visualization/",
          name: "feature-visualization",
        },
        FEATURE_EMBEDDING: {
          path: "/model-explore/:projectUUID?/:modelUUID?/feature-embedding/",
          name: "feature-embedding",
        },
        FEATURE_SUMMARY: {
          path: "/model-explore/:projectUUID?/:modelUUID?/feature-summary/",
          name: "feature-summary",
        },
        MODEL_SUMMARY: {
          path: "/model-explore/:projectUUID?/:modelUUID?/model-summary/",
          name: "model-summary",
        },
        PIPELINE_SUMMARY: {
          path: "/model-explore/:projectUUID?/:modelUUID?/pipeline-summary/",
          name: "pipeline-summary",
        },
        KNOWLEDGE_PACK_SUMMARY: {
          path: "/model-explore/:projectUUID?/:modelUUID?/knowledge-pack-summary/",
          name: "knowledge-pack-summary",
        },
      },
    },
    MODEL_TEST: {
      path: "/model-test/:projectUUID?/:modelUUID?/",
      name: "model-test",
    },
    MODEL_DOWNLOAD: {
      path: "/model-download/:projectUUID?/:modelUUID?/",
      name: "model-download",
    },
    MODEL_SELECT: {
      path: "/model-select/:selectionMode(model-explore|model-test|model-download|change)?/",
      name: "model-select",
      MODES: {
        SELECT_EXPLORE: "model-explore",
        SELECT_TEST: "model-test",
        SELECT_DOWNLOAD: "model-download",
        CHANGE: "change",
      },
    },
  },
};
