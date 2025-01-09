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

import { loadCapture, updateCapturesStatisticsSegments } from "store/captures/actions";
import {
  loadCaptureLabels,
  createCaptureLabels,
  clearCaptureLabels,
  updateCaptureLabels,
  deleteCaptureLabels,
} from "store/captureLabels/actions";
import { setHasUnsavedChanges } from "store/common/actions";
import { createSession } from "store/sessions/actions";
import { setSelectedLabel, createLabelValue } from "store/labels/actions";

import getCaptureLabelsRequestData from "store/captureLabels/domain/getCaptureLabelsRequestData";
import { selectCapture, selectCaptureSensorData } from "store/captures/selectors";

import { selectCaptureLabels } from "store/captureLabels/selectors";
import { selectLabelValues, setSelectedLabelUUID } from "store/labels/selectors";
import { selectedCaptureMetadataParameters } from "store/captureMetadata/selectors";
import { selectSelectedSessionUUID } from "store/sessions/selectors";

import TheCaptureDetailsScreen from "./TheCaptureDetailsScreen";

const mapStateToProps = (state) => {
  return {
    selectCapture: (captureUUID) => selectCapture(captureUUID)(state),
    selectCaptureMetadataParams: (captureUUID) =>
      selectedCaptureMetadataParameters(captureUUID)(state),
    sensorData: selectCaptureSensorData(state),
    selectDefaultCaptureLabels: (sessionUUID, labelUUID) =>
      selectCaptureLabels(state)(sessionUUID, labelUUID),
    captureLabels: state.captureLabels?.data || [],
    sensorList: state.sources.data || [],
    selectedSessionUUID: selectSelectedSessionUUID(state),
    selectedLabelUUID: setSelectedLabelUUID(state),
    labels: state.labels.data || [],
    selectLabelValues: (labelUUID) => selectLabelValues(labelUUID)(state) || [],
    isLoadingSensorData: state?.captures?.captureSensorData?.isFetching || false,
    isLoadingLabel: state?.captures?.captureLabels?.isFetching || false,
    getCaptureLabelsRequestData: (captureUUID, labelUUID, updatedLabelData, deletedLabels) =>
      getCaptureLabelsRequestData(captureUUID, labelUUID, updatedLabelData, deletedLabels)(state),
  };
};

const mapDispatchToProps = {
  loadCapture,
  loadCaptureLabels,
  clearCaptureLabels,
  createCaptureLabels,
  createSession,
  createLabelValue,
  updateCaptureLabels,
  deleteCaptureLabels,
  setHasUnsavedChanges,
  setSelectedLabel,
  updateCapturesStatisticsSegments,
};

export default connect(mapStateToProps, mapDispatchToProps)(TheCaptureDetailsScreen);
