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

import { loadPipelines } from "store/pipelines/actions";
import { loadQueries } from "store/queries/actions";
import { loadSessions } from "store/sessions/actions";
import { loadLabels } from "store/labels/actions";
import { loadMetadata } from "store/metadata/actions";
import { loadSources } from "store/sources/actions";
import { loadPlots } from "store/plots/actions";
import { loadCapturesStatistics } from "store/captures/actions";
import { loadKnowledgepacks } from "store/knowledgepacks/actions";
import { loadCaptureConfigurations } from "store/captureConfigurations/actions";
import { loadFeatureFiles } from "store/featurefiles/actions";
import { setIsMainScreenLoading } from "store/common/actions";
import { loadModels } from "store/models/actions";

const loadProjectData = (projectUUID, isLoadAllModels) => async (dispatch) => {
  dispatch(setIsMainScreenLoading(true));

  await Promise.all([
    dispatch(loadLabels(projectUUID)),
    dispatch(loadMetadata(projectUUID)),
    dispatch(loadSources(projectUUID)),
  ]);

  dispatch(setIsMainScreenLoading(false));

  dispatch(loadSessions(projectUUID));
  dispatch(loadQueries(projectUUID));
  dispatch(loadPipelines(projectUUID));
  dispatch(loadPlots(projectUUID));
  dispatch(loadCapturesStatistics(projectUUID));
  dispatch(loadFeatureFiles(projectUUID));
  dispatch(loadKnowledgepacks(projectUUID));
  dispatch(loadCaptureConfigurations(projectUUID));
  if (isLoadAllModels) {
    dispatch(loadModels(projectUUID));
  }
};

export default loadProjectData;
