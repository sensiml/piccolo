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

import { connect } from "react-redux";

import getCaptureMetadataFormData from "store/captureMetadata/domain/getCaptureMetadataFormData";
// eslint-disable-next-line max-len
import getCaptureConfigurationFormData from "store/captures/domain/getCaptureConfigurationFormData";

import { loadCapturesMetadata, updateCapturesMetadata } from "store/captureMetadata/actions";
import { loadSources } from "store/sources/actions";
import {
  loadCapture,
  loadCapturesStatistics,
  deleteCapture,
  uploadCapture,
  updateCapture,
} from "store/captures/actions";
import { selectCapturesStatistics } from "store/captures/selectors";
import { selectedSampleRate } from "store/captureConfigurations/selectors";
import { selectMetadataTableColumnData } from "store/metadata/selectors";
import { selectSelectedSessionUUID } from "store/sessions/selectors";

import TheCapturesScreen from "./TheCapturesScreen";

const mapStateToProps = (state) => {
  return {
    captures: selectCapturesStatistics(state),
    getCaptureMetadataFormData: (captureUUID) => getCaptureMetadataFormData(state, captureUUID),
    getCaptureConfigurationFormData: (captureUUID) =>
      getCaptureConfigurationFormData(state, captureUUID),
    getSampleRate: (uuid) => selectedSampleRate(uuid)(state),
    selectedSessionUUID: selectSelectedSessionUUID(state),
    metadataTableColumnData: selectMetadataTableColumnData(state),
    isLoadingMetadata: state.metadata?.isFetching || false,
  };
};

const mapDispatchToProps = {
  loadCapturesMetadata,
  updateCapturesMetadata,
  uploadCapture,
  updateCapture,
  loadCapture,
  loadCapturesStatistics,
  loadSources,
  deleteCapture,
};

export default connect(mapStateToProps, mapDispatchToProps)(TheCapturesScreen);
