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

/* eslint-disable max-len */
import React, { useState, useEffect } from "react";
import _ from "lodash";
import { Box } from "@mui/material";
import ConfusionMatrix from "components/ConfusionMatrix";

const ConfusionMatrixSummary = ({ model }) => {
  const [validationData, setValidationData] = useState({
    data: null,
    isFetching: model.isFetching,
  });
  const [trainingData, setTrainingData] = useState({
    data: null,
    isFetching: model.isFetching,
  });
  const [allConfusionMatrix, setAllConfusionMatrix] = useState({
    data: null,
    isFetching: model.isFetching,
  });

  useEffect(() => {
    if (!model.isFetching) {
      setValidationData({
        data: model?.data?.model_results?.metrics?.validation?.ConfusionMatrix,
        isFetching: false,
      });
      setTrainingData({
        data: model?.data?.model_results?.metrics?.train?.ConfusionMatrix,
        isFetching: false,
      });

      if (model?.data?.model_results?.metrics?.AllConfusionMatrix) {
        setAllConfusionMatrix({
          data: model?.data?.model_results?.metrics?.AllConfusionMatrix,
          isFetching: false,
        });
      }
    }
  }, [model]);

  return (
    <Box>
      <Box sx={{ flexWrap: "wrap", display: "flex" }}>
        {!_.isNil(validationData && validationData.data) ? (
          <ConfusionMatrix model={validationData} showTitle={true} modelName="Validation" />
        ) : (
          <></>
        )}
        {!_.isNil(trainingData && trainingData.data) ? (
          <ConfusionMatrix model={trainingData} showTitle={true} modelName="Training" />
        ) : (
          <></>
        )}
      </Box>
      {allConfusionMatrix.data !== null
        ? Object.entries(allConfusionMatrix.data).map(([key, value]) => (
            <Box key={key} sx={{ flexWrap: "wrap", display: "flex" }}>
              <ConfusionMatrix
                model={{ data: value.validation, isFetching: false }}
                showTitle={true}
                modelName={key}
                fileName="validation"
              />
              <ConfusionMatrix
                model={{ data: value.train, isFetching: false }}
                showTitle={true}
                modelName={key}
                fileName="train"
              />
            </Box>
          ))
        : null}
    </Box>
  );
};

export default ConfusionMatrixSummary;
