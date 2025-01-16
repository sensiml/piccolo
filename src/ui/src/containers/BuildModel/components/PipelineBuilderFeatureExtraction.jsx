import React, { useMemo } from "react";
import _ from "lodash";
import { PIPELINE_STEP_TYPES, PIPELINE_GROUPS } from "store/autoML/const";

import PipelineBuilderV1 from "components/PipelineBuilderV1";

const PipelineBuilderClassification = (props) => {
  const { selectedSteps, pipelineData } = props;

  const getFilteredSelectedSteps = useMemo(() => {
    const isStepCached = (pipelineStep, pipelineStepCache) => {
      if (!pipelineStep || !pipelineStepCache) {
        return false;
      }
      if (pipelineStepCache?.name !== pipelineStep.name) {
        return false;
      }
      if (!_.isEmpty(pipelineStep?.set)) {
        return _.isEqual(pipelineStep?.set, pipelineStepCache?.set);
      }

      return _.isEqual(pipelineStep?.inputs, pipelineStepCache?.inputs);
    };

    const getStepType = (isAfterFeatureGenerator) => {
      if (isAfterFeatureGenerator) {
        return PIPELINE_GROUPS.FEATURE_EXTRACTOR.type;
      }
      return PIPELINE_GROUPS.PREPROCESSING.type;
    };

    if (!_.isEmpty(selectedSteps) && !_.isEmpty(pipelineData)) {
      let isStepCacheChanged = false;
      let isAfterFeatureGenerator = false;
      // TODO fix ["Classifier", "Training Algorithm", "Validation Method"].
      const res = selectedSteps
        .filter(
          (step) =>
            !step?.options?.isSessionSegmenter &&
            !["Classifier", "Training Algorithm", "Validation Method"].includes(step?.type),
        )
        .map((step, index) => {
          const pipelineStep = pipelineData?.pipeline ? pipelineData?.pipeline[index] : {};
          const pipelineStepCache = pipelineData?.cache?.pipeline[index];

          const getOutputCacheData = () => {
            const cachedItemsObj = {};
            const outputName = pipelineStep?.outputs[0];
            let isHasDistributionData = false;

            if (outputName) {
              const cacheItems = _.isArray(pipelineData?.cache?.data[outputName])
                ? pipelineData?.cache?.data[outputName]
                : [pipelineData?.cache?.data[outputName]];

              cacheItems.forEach((obj, indexPage) => {
                if (
                  !_.isEmpty(obj.distribution_segments) ||
                  !_.isEmpty(obj.distribution_feature_vectors) ||
                  !_.isEmpty(obj.distribution_samples)
                ) {
                  isHasDistributionData = true;
                }
                cachedItemsObj[obj.filename] = {
                  indexStep: index,
                  indexPage,
                  stepName: step.name,
                  distributionSegments: obj.distribution_segments,
                  distributionFeatureVectors: obj.distribution_feature_vectors,
                  distributionSamples: obj.distribution_samples,
                };
              });
            }
            return [cachedItemsObj, isHasDistributionData];
          };
          // feature_columns
          let isCached = false;
          if (isStepCached(pipelineStep, pipelineStepCache)) {
            isCached = true;
          } else {
            isStepCacheChanged = true;
          }
          if (step.type === PIPELINE_STEP_TYPES.FEATURE_GENERATOR) {
            isAfterFeatureGenerator = true;
          }

          let cacheData = {};
          let isHasDistributionData = false;

          if (isCached && !isStepCacheChanged) {
            [cacheData, isHasDistributionData] = getOutputCacheData();
          }

          return {
            ...step,
            index,
            options: {
              isCached: isCached && !isStepCacheChanged, // all next cache steps are ignored
              cacheData,
              isHasDistributionData,
              type: getStepType(isAfterFeatureGenerator),
              isAfterFeatureGenerator,
              ...step.options,
            },
          };
        });

      return res;
    }
    return [];
  }, [selectedSteps, pipelineData]);

  return (
    <>
      <PipelineBuilderV1 {...props} isModel={false} selectedSteps={getFilteredSelectedSteps} />
    </>
  );
};

export default PipelineBuilderClassification;
