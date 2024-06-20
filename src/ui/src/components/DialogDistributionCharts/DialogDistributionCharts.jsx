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

import React, { useState, useMemo } from "react";
import _ from "lodash";
import { Box } from "@mui/material";

import DialogInformation from "components/DialogInformation";

import { BoxChart } from "components/UICharts";
import { useWindowResize } from "hooks";
import { RESPONSIVE } from "consts";

const DialogDistributionCharts = ({ isOpen, onClose, data, labelColors = {} }) => {
  const [chartWidth, setChartWidth] = useState();

  const DISTRIBUTION_TYPES = [
    "distributionSegments",
    "distributionFeatureVectors",
    "distributionSamples",
  ];

  const DISTRIBUTION_TYPE_TITLES = {
    distributionSegments: "Distribution by Segments",
    distributionSamples: "Distribution by Samples",
    distributionFeatureVectors: "Distribution by Feature Vectors",
  };

  const getChartData = (dataKey) => {
    return _.values(data).reduce((acc, el) => {
      _.entries(el[dataKey]).forEach(([key, value]) => {
        if (acc[key]) {
          acc[key] += value;
        } else {
          acc[key] = value;
        }
      });
      return acc;
    }, {});
  };

  const dataChart = useMemo(() => {
    return DISTRIBUTION_TYPES.reduce((acc, typeKey) => {
      const _dataChart = getChartData(typeKey);
      if (!_.isEmpty(_dataChart)) {
        acc.push({
          key: typeKey,
          title: DISTRIBUTION_TYPE_TITLES[typeKey],
          data: _dataChart,
        });
      }
      return acc;
    }, []);
  }, [data]);

  useWindowResize((windowData) => {
    if (windowData.innerWidth > RESPONSIVE.WIDTH_FOR_TABLET_TEXT) {
      setChartWidth(800);
    } else {
      setChartWidth(windowData.innerWidth * 0.8);
    }
  });

  return (
    <DialogInformation maxWidth={"lg"} isOpen={isOpen} onClose={onClose}>
      <Box mt={4}>
        {dataChart.map((chartObj) => {
          return (
            <Box>
              <BoxChart
                id={chartObj.key}
                key={chartObj.key}
                title={chartObj.title}
                width={chartWidth}
                height={400}
                data={[
                  {
                    y: _.values(chartObj.data),
                    x: _.keys(chartObj.data),
                    marker: {
                      color: _.keys(chartObj.data).map((l) => labelColors[l]),
                      opacity: 0.8,
                    },
                    type: "bar",
                  },
                ]}
              />
            </Box>
          );
        })}
      </Box>
    </DialogInformation>
  );
};

export default DialogDistributionCharts;
