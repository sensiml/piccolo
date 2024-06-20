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

import React, { useMemo } from "react";
import Plot from "react-plotly.js";

const NeuralNetworkSummary = ({ model }) => {
  const plotData = useMemo(() => {
    const trainingMetrics = model?.data?.model_results?.training_metrics;
    const numEpochs = trainingMetrics?.accuracy?.length;
    const epochs = Array.from({ length: numEpochs }, (_, index) => index);
    const numQatEpochs = trainingMetrics?.qat_accuracy?.length;
    const qatEpochs = Array.from({ length: numQatEpochs }, (_, index) => index + numEpochs);
    let dataAccuracy = [];
    let dataLoss = [];

    if (trainingMetrics?.accuracy) {
      dataAccuracy = dataAccuracy.concat([
        {
          x: epochs,
          y: trainingMetrics.accuracy,
          name: "training accuracy",
          line: {
            dash: "solid",
            color: "#1f77b4",
          },
        },
        {
          x: epochs,
          y: trainingMetrics.val_accuracy,
          name: "validation accuracy",
          line: {
            dash: "solid",
            color: "#ff7f0e",
          },
        },
      ]);

      dataLoss = dataLoss.concat([
        {
          x: epochs,
          y: trainingMetrics.loss,
          name: "training loss",
        },
        {
          x: epochs,
          y: trainingMetrics.val_loss,
          name: "validation loss",
        },
      ]);
    }

    if (trainingMetrics?.qat_accuracy) {
      dataAccuracy = dataAccuracy.concat([
        {
          x: qatEpochs,
          y: trainingMetrics.qat_accuracy,
          name: "QAT training accuracy",
          mode: "lines+markers",
          line: {
            dash: "dot",
            color: "#1f77b4",
          },
          marker: {
            symbol: "circle-open",
            size: 8,
          },
        },
        {
          x: qatEpochs,
          y: trainingMetrics.qat_val_accuracy,
          name: "QAT validation accuracy",
          mode: "lines+markers",
          line: {
            dash: "dot",
            color: "#ff7f0e",
          },
          marker: {
            symbol: "circle-open",
            size: 8,
          },
        },
      ]);

      dataLoss = dataLoss.concat([
        {
          x: qatEpochs,
          y: trainingMetrics.qat_loss,
          name: "QAT training loss",
          mode: "lines+markers",
          line: {
            dash: "dot",
            color: "#1f77b4",
          },
          marker: {
            symbol: "circle-open",
            size: 8,
          },
        },
        {
          x: qatEpochs,
          y: trainingMetrics.qat_val_loss,
          name: "QAT validation loss",
          mode: "lines+markers",
          line: {
            dash: "dot",
            color: "#ff7f0e",
          },
          marker: {
            symbol: "circle-open",
            size: 8,
          },
        },
      ]);
    }
    return {
      metrics: trainingMetrics,
      accuracy: dataAccuracy,
      loss: dataLoss,
    };
  }, [model]);

  return (
    <div key="neural_network_summary">
      {!plotData.metrics.accuracy ? null : (
        <div key="neuarl_network_plots" style={{ width: "100%", position: "relative" }}>
          <Plot
            data={plotData.accuracy}
            style={{ width: "100%", height: "100%" }}
            layout={{ title: "Accuracy", xaxis: { title: { text: "Epochs" } } }}
          />
          <Plot
            data={plotData.loss}
            style={{ width: "100%", height: "100%" }}
            layout={{ title: "Loss", xaxis: { title: { text: "Epochs" } } }}
          />
        </div>
      )}
    </div>
  );
};

export default NeuralNetworkSummary;
