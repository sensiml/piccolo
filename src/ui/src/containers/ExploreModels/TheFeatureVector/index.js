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

import { loadFeatureVectorData } from "store/models/actions";
import { loadSegments } from "store/segments/actions";

import { selectSegments } from "store/segments/selectors";
import { selectLabelValuesHashMap, selectLabelValuesColors } from "store/labels/selectors";

import TheFeatureVector from "./TheFeatureVector";

const mapStateToProps = (state) => {
  return {
    modelData: state.models.modelData?.data,
    featureVectorData: state.models.featureVectors?.data,
    featureFileUUID: state.models.featureVectors?.featureFileUUID,
    isFetchingFeatureVectorData: state.models.featureVectors?.isFetching,
    segments: selectSegments(state),
    labelValuesHashMap: selectLabelValuesHashMap()(state),
    selectLabelColorHashMap: (labelName) => selectLabelValuesColors(labelName)(state),
  };
};

const mapDispatchToProps = {
  loadFeatureVectorData,
  loadSegments,
};

export default connect(mapStateToProps, mapDispatchToProps)(TheFeatureVector);
