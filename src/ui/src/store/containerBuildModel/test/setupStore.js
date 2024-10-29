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

import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";

import transforms from "store/transforms/fixtures/transforms";
import mockPipelineStepData from "store/containerBuildModel/fixtures/mockPipelineStepData";
import mockLabels from "store/labels/fixtures/mockLabels";
import mockPipeline from "store/pipelines/fixtures/mockPipeline";
import mockQueryList from "store/queries/fixtures/mockQueryList";
import mockPipelineHierarchyRules from "store/autoML/fixures/mockPipelineHierarchyRules";
import mockMetadata from "store/metadata/fixtures/mockMetadata";

const mockStore = configureMockStore([thunk]);

const setupMockStore = (customStore = {}) =>
  mockStore({
    transforms: {
      data: [...transforms],
    },
    containerBuildModel: { ...mockPipelineStepData },
    labels: { ...mockLabels },
    pipelines: { ...mockPipeline },
    queries: {
      queryList: { ...mockQueryList },
    },
    autoML: {
      pipelineHierarchyRules: mockPipelineHierarchyRules,
    },
    metadata: mockMetadata,
    ...customStore,
  });

export default setupMockStore;
