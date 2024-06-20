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

/* eslint-disable camelcase */
import _ from "lodash";
import {
  PIPELINE_STEP_TYPES,
  TVO_LIST,
  TRANSFORM_TYPES,
  TRANSFORM_LIST,
  AUTOML_SEARCHED_STEPS,
} from "store/autoML/const";
// eslint-disable-next-line max-len
import AbstractStepData from "store/containerBuildModel/domain/PipelineStepsDataFactory/AbstractStepData";

const TYPES = {
  QUERY: "query",
  FEATURE_FILE: "featurefile",
  TRANSFORM: "transform",
  AUGMENTATION_SET: "augmentationset",
  SAMPLER: "sampler",
  GENERATOR_SET: "generatorset",
  SELECTOR_SET: "selectorset",
  TVO: "tvo",
  SEGMENTER: "segmenter",
};

const STEP_TYPES_TO_TYPES = {
  [PIPELINE_STEP_TYPES.SEGMENTER]: TYPES.SEGMENTER,
  [PIPELINE_STEP_TYPES.TRANSFORM]: TYPES.TRANSFORM,
  [PIPELINE_STEP_TYPES.SAMPLER]: TYPES.SAMPLER,
};

const STEP_NAME_TO_PPL_NAME = {
  "Feature Selector": "selector_set",
  "Feature Generator": "generator_set",
  Augmentation: "augmentation_set",
};

const FEATURE_QUANTITION = "Feature Quantization";

const OUTPUTS = {
  generatorset: "generator_set",
  selectorset: "selector_set",
  augmentationset: "augmentation_set",
};

const DEFAULT_SEED = "Custom";
const DEFAULT_TEMP = "temp.raw";

class PipelineDataComposer {
  TRANSFORM_PARSER = [...TRANSFORM_LIST];

  TVO_PARSER = [...TVO_LIST];

  constructor(pipelineSteps, isAutoML, queryData, featureTransformColumns, segmentColumns) {
    /* state */
    this.labelColumn = queryData?.label_column || "";
    this.groupColumns = _.union(queryData?.metadata_columns || [], [this.labelColumn]);
    this.featureTransformColumns = featureTransformColumns || [];
    this.segmentColumns = segmentColumns || [];
    this.pipelineSteps = [...pipelineSteps];
    this.pipelineList = [];
    this.autoMLSeed = {
      seed: DEFAULT_SEED,
      params: {
        reset: true,
      },
    };
    this.isAutoML = isAutoML;
    this.tempIndexes = {};
  }

  __rebuildGroupColumnsWithSegmenter() {
    // if (this.pipelineSteps.indexOf(step => step?.options?.isSessionSegmenter) === -1) {
    // if segmenter is not from session
    // keep uniquue values
    this.groupColumns = _.union(this.groupColumns, this.segmentColumns);
    // }
  }

  __rebuildGroupColumnsWithFeatureTransform() {
    // keep uniquue values
    this.groupColumns = _.union(this.groupColumns, this.featureTransformColumns);
  }

  __getStepName(name) {
    /* get pipeline name from step customName */
    return STEP_NAME_TO_PPL_NAME[name] || name;
  }

  __getTempIndex(nameKey, prefix) {
    // this.tempIndexes =
    if (_.isUndefined(this.tempIndexes[`${nameKey}_${prefix}`])) {
      this.tempIndexes[`${nameKey}_${prefix}`] = 0;
    } else {
      this.tempIndexes[`${nameKey}_${prefix}`] += 1;
    }
    return this.tempIndexes[`${nameKey}_${prefix}`];
  }

  __getTemp(name, { isFeatureOn }) {
    /* get temp object */
    if (name) {
      const nameKey = name.split(" ").join("_");
      const prefix = isFeatureOn ? "temp.features" : "temp";
      const indexTemp = this.__getTempIndex(nameKey, prefix);
      return `${prefix}.${nameKey}${indexTemp}`;
    }
    return DEFAULT_TEMP;
  }

  __getOutputs(name, isFeatureOn) {
    /* builds outputs array */
    const outputs = [this.__getTemp(name, { isFeatureOn: false })];
    if (isFeatureOn) {
      outputs.push(this.__getTemp(name, { isFeatureOn }));
    }
    return outputs;
  }

  __getInputData(prevPipeline) {
    /* builds inputdata */
    const { outputs } = prevPipeline;
    if (outputs) {
      if (Array.isArray(outputs) && outputs?.length) {
        return outputs[0];
      }
      // if string
      return outputs;
    }
    return DEFAULT_TEMP;
  }

  __getFeatureTable(prevPipeline) {
    /* builds feature table */
    const { outputs } = prevPipeline;
    if (outputs) {
      if (Array.isArray(outputs) && outputs?.length > 1) {
        return outputs[1];
      }
      // if string
      return outputs;
    }
    return DEFAULT_TEMP;
  }

  __getGroupColumnsWithSegmenter() {
    // if segmenter is not from session
    // keep uniquue values
    return _.union(this.groupColumns, this.segmentColumns);
  }

  __parseQueryStep(pipelineStep) {
    this.pipelineList.push({
      name: pipelineStep.customName,
      use_session_preprocessor: pipelineStep?.data?.use_session_preprocessor,
      type: TYPES.QUERY,
      outputs: [DEFAULT_TEMP],
    });
  }

  __parseInputDataStep(pipelineStep) {
    this.pipelineList.push({
      name: pipelineStep.customName,
      type: TYPES.FEATURE_FILE,
      outputs: [DEFAULT_TEMP],
      ...pipelineStep.data,
    });
  }

  __parsePipelineData(pipelineData) {
    const INPUT_FEATURE_MIN_MAX_DEFAULTS = "feature_min_max_defaults";
    const LOOKOUP_WITH_QUERY_METADATA = ["passthrough_columns", "group_columns"];
    // TODO add parser
    // remove isServiceField
    return _.entries(pipelineData)
      .filter(([elKey, _elVal]) => !_.includes(elKey, "is_use"))
      .reduce((acc, [name, val]) => {
        if (pipelineData[AbstractStepData.getIsUseParamName(name)] === false) {
          // in case when isUse params === false it means that
          // this value unselected - we don't use current param
          acc[name] = undefined;
          return acc;
        }
        if (LOOKOUP_WITH_QUERY_METADATA.includes(name)) {
          acc[name] = this.groupColumns;
        } else if (INPUT_FEATURE_MIN_MAX_DEFAULTS === name) {
          acc[name] = val?.length === 2 ? { minimum: val[0], maximum: val[1] } : null;
        } else {
          acc[name] = val;
        }
        return acc;
      }, {});
  }

  __parseTransformDataStep(pipelineStep, prevPipeline, isFeatureOn) {
    // eslint-disable-next-line no-unused-vars
    const { transform, input_data, ...pipelineData } = pipelineStep?.data || {};

    const pipelineObj = {
      name: pipelineStep.customName,
      type: STEP_TYPES_TO_TYPES[pipelineStep.type] || TYPES.TRANSFORM,
      outputs: this.__getOutputs(
        OUTPUTS[pipelineStep.customName] || pipelineStep.customName,
        isFeatureOn,
      ),
      inputs: {
        ...this.__parsePipelineData(pipelineData),
        input_data: this.__getInputData(prevPipeline),
      },
    };

    if (isFeatureOn && this.__getFeatureTable(prevPipeline) !== DEFAULT_TEMP) {
      pipelineObj.feature_table = this.__getFeatureTable(prevPipeline);
    }

    this.pipelineList.push(pipelineObj);
  }

  __parseFeatureGeneratorDataStep(pipelineStep, prevPipeline, isFeatureOn) {
    const featureList = pipelineStep?.data || [];
    this.pipelineList.push({
      name: this.__getStepName(pipelineStep.customName),
      type: TYPES.GENERATOR_SET,
      outputs: this.__getOutputs(OUTPUTS[TYPES.GENERATOR_SET], isFeatureOn),
      inputs: {
        input_data: this.__getInputData(prevPipeline),
        group_columns: this.groupColumns || [],
      },
      // only false means that isSelected is unselected
      set: featureList
        .filter((feature) => feature.isSelected !== false)
        .map((feature) => ({
          function_name: feature.name,
          inputs: { ...feature.params },
        })),
    });
  }

  __parseFeatureSelectorDataStep(pipelineStep, prevPipeline, isFeatureOn) {
    this.pipelineList.push({
      name: this.__getStepName(pipelineStep.customName),
      type: TYPES.SELECTOR_SET,
      outputs: this.__getOutputs(OUTPUTS[TYPES.SELECTOR_SET], isFeatureOn),
      refinement: {},
      inputs: {
        number_of_features: 10,
        remove_columns: [],
        cost_function: "sum",
        label_column: this.labelColumn || "",
        passthrough_columns: this.groupColumns || [],
        feature_table: this.__getFeatureTable(prevPipeline),
        input_data: this.__getInputData(prevPipeline),
      },
      set: pipelineStep?.data?.map((feature) => ({
        function_name: feature.name,
        inputs: { ...feature.params },
      })),
    });
  }

  __parseAugmentationDataStep(pipelineStep, prevPipeline, isFeatureOn) {
    this.pipelineList.push({
      name: this.__getStepName(pipelineStep.name),
      type: TYPES.AUGMENTATION_SET,
      label_column: this.labelColumn || "",
      outputs: this.__getOutputs(OUTPUTS[TYPES.AUGMENTATION_SET], isFeatureOn),
      inputs: {
        label_column: this.labelColumn || "",
        group_columns: this.__getGroupColumnsWithSegmenter() || [],
        passthrough_columns: this.__getGroupColumnsWithSegmenter() || [],
        input_data: this.__getInputData(prevPipeline),
      },
      set: pipelineStep?.data?.map((feature) => ({
        function_name: feature.name,
        inputs: { ...feature.params },
      })),
    });
  }

  __parseTVODataStep(pipelineStep, prevPipeline, isFeatureOn) {
    const parseData = (data) => {
      if (data?.length) {
        return data.map((el) => {
          const { transform: name, ...inputs } = el;
          return { name, inputs };
        });
      }
      if (data) {
        const { transform: name, ...inputs } = data;
        return [{ name, inputs }];
      }
      return [];
    };

    let indexTVO = this.pipelineList.findIndex((ppl) => ppl.type === TYPES.TVO);
    if (indexTVO < 0) {
      //
      this.pipelineList.push({
        name: TYPES.TVO,
        type: TYPES.TVO,
        outputs: this.__getOutputs(TYPES.TVO, isFeatureOn),
        feature_table: this.__getFeatureTable(prevPipeline),
        validation_seed: 0,
        label_column: this.labelColumn || "",
        ignore_columns: this.groupColumns.filter((col) => col !== this.labelColumn) || [],
        input_data: this.__getInputData(prevPipeline),
        validation_methods: [],
        classifiers: [],
        optimizers: [],
      });
      indexTVO = this.pipelineList.findIndex((ppl) => ppl.type === TYPES.TVO);
    }
    if (pipelineStep.type === PIPELINE_STEP_TYPES.CLASSIFIER) {
      this.pipelineList[indexTVO].classifiers = parseData(pipelineStep.data);
    }
    if (pipelineStep.type === PIPELINE_STEP_TYPES.TRAINING_ALGORITHM) {
      this.pipelineList[indexTVO].optimizers = parseData(pipelineStep.data);
    }
    if (pipelineStep.type === PIPELINE_STEP_TYPES.VALIDATION) {
      this.pipelineList[indexTVO].validation_methods = parseData(pipelineStep.data);
    }
  }

  __parseAutoMLParamsDataStep(pipelineStep) {
    const { data } = pipelineStep || {};

    if (data) {
      // eslint-disable-next-line camelcase
      const { tvo, selectorset, set_training_algorithm, set_selectorset, ...restData } = data;
      let trainingAlgorithms;
      let selectorSet;
      if (set_training_algorithm?.length) {
        trainingAlgorithms = set_training_algorithm.reduce((acc, algo) => {
          acc[algo] = {};
          return acc;
        }, {});
      }
      if (set_selectorset?.length) {
        selectorSet = set_selectorset.reduce((acc, selector) => {
          acc[selector] = {};
          return acc;
        }, {});
      }

      const searchSteps = [];
      if (tvo) {
        searchSteps.push(AUTOML_SEARCHED_STEPS.TVO_PARAM);
      }
      if (selectorset) {
        searchSteps.push(AUTOML_SEARCHED_STEPS.SELECTOR_SET_PARAM);
      }
      if (trainingAlgorithms) {
        Object.assign(this.autoMLSeed.params, { set_training_algorithm: trainingAlgorithms });
      }
      if (selectorSet) {
        Object.assign(this.autoMLSeed.params, { set_selectorset: selectorSet });
      }
      Object.assign(this.autoMLSeed.params, { ...restData, search_steps: [...searchSteps] });
    }
  }

  __parsePipelineSteps() {
    let prevPipeline = {};
    let isFeatureOn = false;
    this.pipelineSteps.forEach((pplStep) => {
      if (pplStep?.type === PIPELINE_STEP_TYPES.QUERY) {
        this.__parseQueryStep(pplStep);
      } else if (pplStep?.type === PIPELINE_STEP_TYPES.INPUT_DATA) {
        this.__parseInputDataStep(pplStep);
      } else if (pplStep?.type === PIPELINE_STEP_TYPES.AUGMENTATION) {
        this.__parseAugmentationDataStep(pplStep, prevPipeline, isFeatureOn);
      } else if (pplStep?.type === PIPELINE_STEP_TYPES.SEGMENTER) {
        // we don't add segmenter if it's isSessionSegmenter,
        if (!pplStep?.options?.isSessionSegmenter) {
          this.__parseTransformDataStep(pplStep, prevPipeline, isFeatureOn);
        }
        //  update group columns if segmenter
        this.__rebuildGroupColumnsWithSegmenter();
      } else if (this.TRANSFORM_PARSER.includes(pplStep?.type)) {
        this.__parseTransformDataStep(pplStep, prevPipeline, isFeatureOn);
        if (pplStep?.name === TRANSFORM_TYPES.FEATURE_TRANSFORM) {
          this.__rebuildGroupColumnsWithFeatureTransform();
        }
      } else if (pplStep?.name === FEATURE_QUANTITION) {
        this.__parseTransformDataStep(pplStep, prevPipeline, isFeatureOn);
      } else if (pplStep?.type === PIPELINE_STEP_TYPES.FEATURE_GENERATOR) {
        isFeatureOn = true;
        this.__parseFeatureGeneratorDataStep(pplStep, prevPipeline, isFeatureOn);
      } else if (pplStep?.type === PIPELINE_STEP_TYPES.FEATURE_SELECTOR) {
        isFeatureOn = true;
        this.__parseFeatureSelectorDataStep(pplStep, prevPipeline, isFeatureOn);
      } else if (this.TVO_PARSER.includes(pplStep?.type)) {
        this.__parseTVODataStep(pplStep, prevPipeline, isFeatureOn, isFeatureOn);
      }
      // save last step
      prevPipeline = this.pipelineList[this.pipelineList.length - 1] || {};
    });
    return this.pipelineList;
  }

  getPipelineData(autoMLParams) {
    /*
      @return {Array} pipelineList, autoMLSeed
    */
    if (!this.pipelineSteps?.length) {
      return [];
    }
    this.__parsePipelineSteps();
    this.__parseAutoMLParamsDataStep(autoMLParams);
    return { pipelineList: this.pipelineList, autoMLSeed: this.autoMLSeed };
  }
}

export default PipelineDataComposer;
