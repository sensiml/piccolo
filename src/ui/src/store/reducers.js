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

import { combineReducers } from "redux";
import { connectRouter } from "connected-react-router";
import TokenStorage from "services/TokenStorage";

import auth from "./auth/reducers";
import autoML from "./autoML/reducers";
import captures from "./captures/reducers";
import captureConfigurations from "./captureConfigurations/reducers";
import captureMetadata from "./captureMetadata/reducers";
import captureLabels from "./captureLabels/reducers";
import common from "./common/reducers";
import containerBuildModel from "./containerBuildModel/reducers";
import downloadModel from "./downloadModel/reducers";
import featurefiles from "./featurefiles/reducers";
import knowledgepacks from "./knowledgepacks/reducers";
import labels from "./labels/reducers";
import metadata from "./metadata/reducers";
import models from "./models/reducers";
import pipelines from "./pipelines/reducers";
import pipelineTemplates from "./pipelineTemplates/reducers";
import platforms from "./platforms/reducers";
import plots from "./plots/reducers";
import projects from "./projects/reducers";
import segments from "./segments/reducers";
import queries from "./queries/reducers";
import sessions from "./sessions/reducers";
import sources from "./sources/reducers";
import team from "./team/reducers";
import transforms from "./transforms/reducers";
import classifiers from "./classifiers/reducers";
import deviceProfiles from "./deviceprofile/reducers";
import platformLogos from "./platformlogos/reducers";
import { RESET_APP, LOG_OUT } from "./auth/actions/actionTypes";

const allReducers = (history) =>
  combineReducers({
    router: connectRouter(history),
    history,
    auth,
    autoML,
    captures,
    captureConfigurations,
    captureMetadata,
    captureLabels,
    classifiers,
    common,
    containerBuildModel,
    downloadModel,
    featurefiles,
    knowledgepacks,
    labels,
    metadata,
    models,
    pipelines,
    pipelineTemplates,
    platforms,
    plots,
    projects,
    queries,
    sessions,
    sources,
    segments,
    team,
    transforms,
    deviceProfiles,
    platformLogos,
  });

const rootReducer = (history) => (state, action) => {
  if ([LOG_OUT, RESET_APP].includes(action.type)) {
    TokenStorage.removeToken();
    TokenStorage.removeRefreshToken();
    const updatedState = {
      auth: { loggedIn: false },
      projects: { lastSelectedProjects: state.projects?.lastSelectedProjects },
      // shoudn't keep router info is user click "Log out"
      router: state.router,
    };
    return { ...updatedState };
  }
  return allReducers(history)(state, action);
};

export default rootReducer;
