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

import _ from "lodash";
import PipelineDataComposer from "../domain/PipelineDataComposer";

// data
import autoMLToCompose from "./data/autoMLToCompose";
import expectedComposedAutoMLPipeline from "./data/expectedComposedAutoMLPipeline";

const collectAllValDFS = (lastVal, lastKey, prevKey, colletedArr) => {
  const setVal = (key, prevKey, val) => {
    // put only not empty values
    if (val) {
      if (prevKey) {
        colletedArr[`${prevKey}_${key}`] = val;
      } else {
        colletedArr[key] = val;
      }
    }
  };

  if (_.isArray(lastVal)) {
    if (lastVal?.length && _.isObject(lastVal[0])) {
      // if obejct array
      Object.entries(lastVal).forEach(([key, val]) => {
        collectAllValDFS(val, key, prevKey ? `${prevKey}_${lastKey}` : lastKey, colletedArr);
      });
    } else {
      // set value
      setVal(lastKey, prevKey, lastVal.sort());
    }
  } else if (_.isObject(lastVal) && !_.isEmpty(lastVal)) {
    Object.entries(lastVal).forEach(([key, val]) => {
      collectAllValDFS(val, key, prevKey ? `${prevKey}_${lastKey}` : lastKey, colletedArr);
    });
  } else {
    // set value
    setVal(lastKey, prevKey, lastVal);
  }
};

describe("PipelineDataComposer.test", () => {
  describe("AutoML pipeline compare with reference", () => {
    const { expPipelineJson, expAutoMLSeed } = expectedComposedAutoMLPipeline;
    const queryData = autoMLToCompose.pipeline[0].options.descriptionParameters;
    const { pipeline, pipelineSettings } = autoMLToCompose;
    const [featureTransformColumns, segmentColumns] = [["CascadeID"], ["SegmentID"]];
    const composer = new PipelineDataComposer(
      pipeline,
      queryData,
      featureTransformColumns,
      segmentColumns,
    );
    const { pipelineList, autoMLSeed } = composer.getPipelineData(pipelineSettings.data);

    expect(_.isEqual(autoMLSeed, expAutoMLSeed)).toEqual(true);

    pipelineList.forEach((composedEl, index) => {
      describe(`comparing ${composedEl.name} ${composedEl.type} with the reference object`, () => {
        const referenceElement = expPipelineJson[index];

        let referenceAllValues = {};
        let composedAllValues = {};

        collectAllValDFS(referenceElement, null, null, referenceAllValues);
        collectAllValDFS(composedEl, null, null, composedAllValues);

        /// "sampler", "featurefile", "segmenter", "transform", "generatorset"
        Object.keys(referenceAllValues).forEach((key) => {
          it(`the ${key} with value ${composedAllValues[key]} should be ${referenceAllValues[key]}`, () => {
            expect(composedAllValues[key]).toEqual(referenceAllValues[key]);
          });
        });
      });
    });
  });
});
