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
import { selectedSessionData, selectedSessionName } from "store/sessions/selectors";
// eslint-disable-next-line no-unused-vars
import { PIPELINE_STEP_TYPES, AUTOML_STEP } from "store/autoML/const";
import { STEP_TYPES } from "store/pipelines/const";
import { DEFAULT_PIPELINE_SETTINGS } from "store/containerBuildModel/domain/PipelineDataDefault";

class PipelineDataDecomposer {
  constructor(state, pipelineData) {
    /* state */
    const { pipeline, ...rest } = pipelineData;
    this.state = state;

    this.pipelineData = rest;
    this.pipelineList = pipeline;

    this.decomposedSteps = [];

    this.queryFromInputData = null;
    this.metadataFromInputData = null;
    this.tvoCount = 0;
  }

  __getRule(name) {
    const hierarchyRules = this.state.autoML.pipelineHierarchyRules.data;
    return hierarchyRules.find((rule) => rule.name === name);
  }

  __getStep(transformType, transformSubtype, transformName) {
    const hierarchyRules = this.state.autoML.pipelineHierarchyRules.data;

    return hierarchyRules.find((rule) => {
      if (rule?.excludeTransform && rule.excludeTransform.includes(transformName)) {
        return false;
      }
      if (rule?.type === transformType && rule?.subtype?.includes(transformSubtype)) {
        return true;
      }
      if (rule?.type === transformType && !rule?.subtype?.length) {
        // some rules don't have subtypes
        return true;
      }
      if (rule?.transformList?.includes(transformName)) {
        return true;
      }
      return false;
    });
  }

  __getTransform(name) {
    const tranformList = this.state?.transforms?.data || [];
    return tranformList.find((trsf) => trsf.name === name) || {};
  }

  __setPipelineStep(name, customName, data, options) {
    const stepsByName = this.decomposedSteps.filter((step) => step.name === name);
    // the same step can bee stored previosly for session steps
    const sameSessionPrevStepIndex = this.decomposedSteps.findIndex((step) => {
      if (step.name === name && step.customName === customName) {
        return options?.isSession ? !step.options?.isSession : false;
      }
      return false;
    });

    const hirerarchyRule = this.__getRule(name);

    let limit = null;
    if (hirerarchyRule) {
      limit = hirerarchyRule.limit || null;
    }

    if (!stepsByName?.length) {
      this.decomposedSteps.push({ name, customName, data, options });
    } else if (limit === null || limit > (stepsByName?.length || 0)) {
      // check limit, if limit == null it's no limit and
      if (sameSessionPrevStepIndex !== -1) {
        this.decomposedSteps[sameSessionPrevStepIndex] = { name, customName, data, options };
      } else {
        this.decomposedSteps.push({ name, customName, data, options });
      }
    }
  }

  __parseFeatureGeneratorStepData(pipelineItem) {
    const { set } = pipelineItem;
    const data = [];
    if (set?.length) {
      set.forEach((setObj) => {
        data.push({
          name: setObj.function_name,
          params: { ...setObj.inputs },
        });
      });
    }
    if (data?.length) {
      this.__setPipelineStep(
        PIPELINE_STEP_TYPES.FEATURE_GENERATOR,
        PIPELINE_STEP_TYPES.FEATURE_GENERATOR,
        data,
      );
    }
  }

  __parseFeatureSelectorStepData(pipelineItem) {
    /* Not used now */
    const { set } = pipelineItem;
    const data = [];
    if (set?.length) {
      set.forEach((setObj) => {
        const { inputs = {} } = setObj;
        data.push({
          name: setObj.function_name,
          params: { ...inputs },
        });
      });
    }
    if (data?.length) {
      this.__setPipelineStep(
        PIPELINE_STEP_TYPES.FEATURE_SELECTOR,
        PIPELINE_STEP_TYPES.FEATURE_SELECTOR,
        data,
      );
    }
  }

  __parseAugmentationStepData(pipelineItem) {
    const { set } = pipelineItem;
    const data = [];
    const names = [];
    if (set?.length) {
      set.forEach((setObj) => {
        const { inputs = {} } = setObj;
        names.push(setObj.function_name);
        data.push({
          name: setObj.function_name,
          params: { ...inputs },
        });
      });
    }
    if (data?.length) {
      this.__setPipelineStep(PIPELINE_STEP_TYPES.AUGMENTATION, _.join(names, ", "), data);
    }
  }

  __parseTransformStepData(pipelineItem) {
    const INPUT_FEATURE_MIN_MAX_DEFAULTS = "feature_min_max_defaults";
    const transform = this.__getTransform(pipelineItem?.name);

    const inputs = _.entries(pipelineItem.inputs).reduce((acc, [inputKey, inputValue]) => {
      if (inputKey === INPUT_FEATURE_MIN_MAX_DEFAULTS) {
        acc[inputKey] = _.values(inputValue); // transform object ot array
      } else {
        acc[inputKey] = inputValue;
      }
      return acc;
    }, {});

    if (transform) {
      const { type, subtype, name } = transform;
      const pipelineStep = this.__getStep(type, subtype, name);
      if (pipelineStep?.name) {
        this.__setPipelineStep(
          pipelineStep.name,
          name,
          { ...inputs, transform: name },
          { ...pipelineItem.options },
        );
      }
    }
  }

  __parseTVOStepData(pipelineItem) {
    if (pipelineItem?.classifiers?.length) {
      this.tvoCount += 1;
      pipelineItem.classifiers.forEach((el) => {
        this.__parseTransformStepData(el);
      });
    }
    if (pipelineItem?.optimizers?.length) {
      this.tvoCount += 1;
      pipelineItem.optimizers.forEach((el) => {
        this.__parseTransformStepData(el);
      });
    }
    if (pipelineItem?.validation_methods?.length) {
      this.tvoCount += 1;
      pipelineItem.validation_methods.forEach((el) => {
        this.__parseTransformStepData(el);
      });
    }
  }

  __parseFeatureFileStepData(pipelineItem) {
    this.queryFromInputData = {
      uuid: "1",
      isExtractedFromInputData: true,
      name: pipelineItem.name,
      label_column: pipelineItem.label_column,
      columns: pipelineItem.data_columns,
      metadata_columns: pipelineItem.group_columns,
    };

    this.metadataFromInputData = {
      id: "1",
      label_values: [],
      metadata: false,
    };

    this.__setPipelineStep(PIPELINE_STEP_TYPES.INPUT_DATA, pipelineItem.name, {
      name: pipelineItem.name,
      label_column: pipelineItem.label_column,
      data_columns: pipelineItem.data_columns,
      group_columns: pipelineItem.group_columns,
    });
  }

  __parseQueryStepData(pipelineItem) {
    const descriptionParameters = _.reduce(
      this.state.queries?.queryList?.data,
      (acc, el) => {
        if (el.name === pipelineItem.name) {
          // eslint-disable-next-line no-param-reassign
          acc = {
            uuid: el.uuid,
            name: el.name,
            label_column: el.label_column,
            columns: el.columns,
            metadata_columns: el.metadata_columns,
            session: selectedSessionName(el.segmenter_id)(this.state),
            cacheStatus: el.task_status,
          };
        }
        return acc;
      },
      {},
    );

    this.__setPipelineStep(
      PIPELINE_STEP_TYPES.QUERY,
      pipelineItem.name,
      {
        name: pipelineItem.name,
        use_session_preprocessor: pipelineItem.use_session_preprocessor,
      }, // data
      { descriptionParameters }, // options
    );
  }

  __parsePipelineItem(pplItem) {
    if (pplItem?.type === STEP_TYPES.QUERY) {
      this.__parseQueryStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.FEATURE_FILE) {
      this.__parseFeatureFileStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.TRANSFORM) {
      this.__parseTransformStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.AUGMENTATION_SET) {
      this.__parseAugmentationStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.SEGMENTER) {
      this.__parseTransformStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.SAMPLER) {
      this.__parseTransformStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.GENERATOR_SET) {
      this.__parseFeatureGeneratorStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.SELECTOR_SET) {
      this.__parseFeatureSelectorStepData(pplItem);
    } else if (pplItem?.type === STEP_TYPES.TVO) {
      this.__parseTVOStepData(pplItem);
    } else {
      this.__parseTransformStepData(pplItem);
    }
  }

  __getSessionObj(sessionObj) {
    try {
      return JSON.parse(sessionObj);
    } catch (e) {
      return {};
    }
  }

  __extractSessionData() {
    const queryStep = this.decomposedSteps.find(
      (pplStep) => pplStep?.name === PIPELINE_STEP_TYPES.QUERY,
    );
    const selectedQuery = this.state?.queries?.queryList?.data?.find(
      (q) => q.name === queryStep?.data?.name,
    );
    if (selectedQuery) {
      const sessionData = selectedSessionData(selectedQuery.segmenter_id)(this.state) || {};
      if (sessionData.parameters) {
        const parameters = this.__getSessionObj(sessionData.parameters);
        this.__parsePipelineItem({
          ...parameters,
          options: { isSession: true, isSessionSegmenter: true },
        });
      }
      // parse preprocess
      if (sessionData.preprocess) {
        const preprocess = this.__getSessionObj(sessionData.preprocess);
        if (Object.keys(preprocess)?.length) {
          Object.values(preprocess).forEach((preprocessObj, index) => {
            if (preprocessObj?.params) {
              this.__parsePipelineItem({
                ...preprocessObj.params,
                options: {
                  isSession: true,
                  isSessionPreprocess: true,
                  uniqueName: `preprocessor_${index}`,
                },
              });
            }
          });
        } else if (preprocess?.params) {
          this.__parsePipelineItem({
            ...preprocess?.params,
            options: {
              isSession: true,
              isSessionPreprocess: true,
              uniqueName: "preprocessor_0",
            },
          });
        }
      }
    }
  }

  __extractAutoMLParams() {
    const APIdata = this?.pipelineData?.hyper_params?.params || {};
    const data = _.entries(DEFAULT_PIPELINE_SETTINGS.params).reduce((acc, [key, defaultValue]) => {
      if (key === "search_steps" && !_.isEmpty(APIdata[key])) {
        _.assign(acc, { selectorset: false, tvo: false });
        APIdata[key].forEach((val) => {
          acc[val] = true;
        });
      } else if (key === "search_steps") {
        // if no search_steps set default params as true
        _.assign(acc, { selectorset: true, tvo: true });
      } else {
        acc[key] = !_.isUndefined(APIdata[key]) ? APIdata[key] : defaultValue;
      }
      return acc;
    }, {});
    // this.__setPipelineStep(AUTOML_STEP.name, AUTOML_STEP.customName, data);
    return data;
  }

  __parsePipelineList() {
    this.pipelineList.forEach((pplItem) => {
      this.__parsePipelineItem(pplItem);
    });
    return this.decomposedSteps;
  }

  get isNeededToAddTVO() {
    return this.tvoCount < 3;
  }

  getPipelineStepData() {
    if (!this.pipelineList?.length) {
      return [];
    }
    return this.__parsePipelineList();
  }

  getSessionStepData(queryName) {
    this.__parseQueryStepData({ name: queryName });
    this.__extractSessionData();
    return this.decomposedSteps.filter((step) => step.customName !== queryName);
  }

  getAutoMLStepData() {
    return this.__extractAutoMLParams();
  }

  getAutoMLStep() {
    return {
      ...AUTOML_STEP,
      data: this.__extractAutoMLParams(),
      options: {},
    };
  }
}

export default PipelineDataDecomposer;
