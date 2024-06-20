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
import { selectedSessionData } from "store/sessions/selectors";
import { PIPELINE_STEP_TYPES, TRANSFORM_TYPES, TVO_LIST } from "store/autoML/const";
import {
  StepDataQuery,
  StepDataTransform,
  StepDataFeatureGenerator,
  StepDataFeatureSelector,
  StepDataTvo,
} from "store/containerBuildModel/domain/PipelineStepsDataFactory";
// eslint-disable-next-line max-len
import combineFeaturesToNumColumns from "store/containerBuildModel/domain/utilCombineFeaturesToNumColumns";

const DEFAULT_STEPS = [
  // We're using snake case style, because potentially it's python API
  {
    name: "Pipeline Settings",
    type: PIPELINE_STEP_TYPES.AUTOML_PARAMS,
    subtypes: [],
    params: {
      disable_automl: false,
      "prediction_target(%)": {
        f1_score: 100,
      },
      hardware_target: {
        classifiers_sram: 32000,
      },
      selectorset: true,
      set_selectorset: [
        "Information Gain",
        "t-Test Feature Selector",
        "Univariate Selection",
        "Tree-based Selection",
      ],
      tvo: true,
      set_training_algorithm: [
        "Hierarchical Clustering with Neuron Optimization",
        "RBF with Neuron Allocation Optimization",
        "Random Forest",
        "xGBoost",
        "Train Fully Connected Neural Network",
      ],
      iterations: 2,
      allow_unknown: false,
      population_size: 40,
      single_model: true,
      hierarchical_multi_model: false,
    },
  },
  {
    type: PIPELINE_STEP_TYPES.QUERY,
    name: "Query",
    options: { is_should_be_reviewed: false },
  },
  {
    type: PIPELINE_STEP_TYPES.SEGMENTER,
    name: PIPELINE_STEP_TYPES.SEGMENTER,
    transform: "Windowing",
    input_contracts: [],
    options: {
      is_should_be_reviewed: true,
      message:
        // eslint-disable-next-line max-len
        "Windowing has been set as the default Segmenter. The default window size is set to 1 second of data for your project. Please review/update the parameters and then click the save button to confirm.",
    },
  },
  {
    type: PIPELINE_STEP_TYPES.FEATURE_GENERATOR,
    name: PIPELINE_STEP_TYPES.FEATURE_GENERATOR,
    subtypes: ["Statistical"],
    options: {
      is_should_be_reviewed: true,
      message:
        // eslint-disable-next-line max-len
        "Feature Generators are used to extract information from the input sensor data. In this form you will be able to specify the types of feature generators you would like to use along with the inputs into the feature generators and any parameters the feature generators take. Some feature generators will produce a single value and some will produce multiple. Some can also take more than one sensor input. You can select up to 250 Feature generators as part of your pipeline. See our documentation for more information about the feature generators.",
    },
    set: [],
    input_contracts: [],
  },
  {
    type: PIPELINE_STEP_TYPES.FEATURE_SELECTOR,
    name: PIPELINE_STEP_TYPES.FEATURE_SELECTOR,
    subtypes: [],
    set: ["Correlation Threshold", "Variance Threshold"],
    input_contracts: {
      "Correlation Threshold": { threshold: 0.95 },
      "Variance Threshold": { threshold: 0.15 },
    },
  },
  {
    type: PIPELINE_STEP_TYPES.TRANSFORM,
    name: "Feature Quantization",
    transform: "Min Max Scale",
    input_contracts: [{ feature_min_max_defaults: [-100, 100] }],
  },
  {
    type: PIPELINE_STEP_TYPES.CLASSIFIER,
    name: PIPELINE_STEP_TYPES.CLASSIFIER,
    transform: "PME",
    input_contracts: [],
  },
  {
    type: PIPELINE_STEP_TYPES.TRAINING_ALGORITHM,
    name: PIPELINE_STEP_TYPES.TRAINING_ALGORITHM,
    transform: "RBF with Neuron Allocation Optimization",
    input_contracts: [],
  },
  {
    type: PIPELINE_STEP_TYPES.VALIDATION,
    name: PIPELINE_STEP_TYPES.VALIDATION,
    transform: "Stratified Shuffle Split",
    input_contracts: [],
  },
];

const DEFAULT_CLASSIFIER_TRAINING_ALGORITHMS = {
  Bonsai: "Bonsai Tree Optimizer",
  PME: "RBF with Neuron Allocation Optimization",
  "Decision Tree Ensemble": "Random Forest",
  "Boosted Tree Ensemble": "xGBoost",
  "TensorFlow Lite for Microcontrollers": "Train Fully Connected Neural Network",
};

class PipelineDataBuilderDefault {
  constructor(state, defaultOptions, queryName) {
    this.state = state;
    this.pipelineSteps = [];
    this.queryName = queryName;
    this.isAfterSegmenter = false;
    this.isAddFeatureTransform = false;
    this.isAddSensorTransform = false;
    this.isAutoMLOptimization = defaultOptions?.isAutoMLOptimization;
    this.selectedClassifier = defaultOptions?.selectedClassifier;
    this.isUseSessionPreprocessor = defaultOptions?.isUseSessionPreprocessor;
    this.prevTransform = "";
    this.reviewedStepsParams = [
      "Name: Windowing",
      "Type: Segmenter",
      "Parameters: Window Size, Delta",
    ];
  }

  __getDefaultFeatureValues(step, ftName, constractName) {
    if (step.input_contracts[ftName] && step.input_contracts[ftName][constractName]) {
      const res = step.input_contracts[ftName][constractName];
      return res;
    }
    return [];
  }

  __setPipelineStep(name, customName, data, options) {
    this.pipelineSteps.push({ name, customName, data, options });
  }

  __populateQuery(step) {
    const stepData = new StepDataQuery({
      state: this.state,
      type: step.type,
    }).getInputsData();
    let data = {};
    let customName = "";

    if (stepData?.length) {
      data = stepData.reduce((acc, el) => {
        if (el.name === "use_session_preprocessor") {
          acc[el.name] = !_.isUndefined(this.isUseSessionPreprocessor)
            ? this.isUseSessionPreprocessor
            : el.default;
        }
        if (el.default) {
          acc[el.name] = el.default;
        } else if (el?.options?.length) {
          customName = this.queryName || el.options[0].value;
          acc[el.name] = this.queryName || el.options[0].value;
        }
        return acc;
      }, {});
    }

    this.queryName = this.queryName || customName;
    const selectedQuery = this.state?.queries?.queryList?.data?.find(
      (q) => q.name === this.queryName,
    );
    if (selectedQuery) {
      const sessionData = selectedSessionData(selectedQuery.segmenter_id)(this.state) || {};
      if (this.isUseSessionPreprocessor && sessionData.parameters) {
        this.reviewedStepsParams = [];
      }
    }

    this.__setPipelineStep(step.name, customName, data, step.options);
  }

  __populateTransform(step) {
    /**
     * Populate transform step
     * */
    const StepDataClass = TVO_LIST.includes(step.type) ? StepDataTvo : StepDataTransform;
    let exactTransform = step.transform;

    if (step.type === PIPELINE_STEP_TYPES.CLASSIFIER) {
      exactTransform = this.selectedClassifier || step.transform;
      this.selectedClassifier = exactTransform;
    }

    if ([PIPELINE_STEP_TYPES.TRAINING_ALGORITHM].includes(step.type)) {
      exactTransform =
        DEFAULT_CLASSIFIER_TRAINING_ALGORITHMS[this.selectedClassifier] || step.transform;
    }

    const stepData = new StepDataClass({
      state: this.state,
      type: step.type,
      isAfterSegment: this.isAfterSegmenter,
      isAddFeatureTransform: this.isAddFeatureTransform,
      isAddSensorTransform: this.isAddSensorTransform,
      queryName: this.queryName,
    }).getInputsData({ exactTransform, prevTransform: this.prevTransform });

    const transform = stepData?.options.find((el) => el.name === exactTransform);

    this.prevTransform = transform?.name;

    let customName = "";
    let data = {};

    if (transform && stepData?.fieldset) {
      customName = transform?.name;
      data = stepData?.fieldset
        .filter((el) => el.parent === transform.name)
        .reduce((acc, el) => {
          acc[el.name] = el.default;
          return acc;
        }, {});
    }
    this.__setPipelineStep(
      step.name,
      customName,
      { ...data, transform: transform?.name },
      step.options,
    );

    if (step.type === PIPELINE_STEP_TYPES.SEGMENTER) {
      this.isAfterSegmenter = true;
    }
    if (step.name === TRANSFORM_TYPES.FEATURE_TRANSFORM) {
      this.isAddFeatureTransform = true;
    }
    if (step.name === TRANSFORM_TYPES.SENSOR_TRANSFORM) {
      this.isAddSensorTransform = true;
    }
  }

  __populateFeatureGenerator(step) {
    const stepData = new StepDataFeatureGenerator({
      state: this.state,
      type: step.type,
      isAfterSegment: this.isAfterSegmenter,
      isAddFeatureTransform: this.isAddFeatureTransform,
      isAddSensorTransform: this.isAddSensorTransform,
      queryName: this.queryName,
    }).getInputsData({});

    const selectedFeatures = stepData.featureList.filter((feature) => {
      return step.subtypes.includes(feature.subtype);
    });
    const selectedFeaturesWithParams = selectedFeatures.map((ft) => {
      let params = {};
      if (ft?.inputContract?.length) {
        params = ft?.inputContract.reduce((accParams, el) => {
          accParams[el.name] = el.default;
          return accParams;
        }, {});
      }
      return { ...ft, params };
    });
    const combinedFeatures = combineFeaturesToNumColumns(selectedFeaturesWithParams);
    const data = combinedFeatures.map((fg) => ({
      name: fg.name,
      params: fg.params,
    }));

    this.__setPipelineStep(step.name, step.name, data, step.options);
  }

  __populateFeatureSelector(step) {
    /**
     * Populate transform step
     * */

    const stepData = new StepDataFeatureSelector({
      state: this.state,
      type: step.type,
      isAfterSegment: this.isAfterSegmenter,
      isAddFeatureTransform: this.isAddFeatureTransform,
      isAddSensorTransform: this.isAddSensorTransform,
      queryName: this.queryName,
    }).getInputsData({});

    const selectedFeatures = stepData.featureList.filter((feature) => {
      return step.set.includes(feature.name);
    });

    const data = selectedFeatures.map((ft) => {
      let params = {};
      if (ft?.inputContract?.length) {
        params = ft?.inputContract.reduce((accParams, el) => {
          const defaultValue = this.__getDefaultFeatureValues(step, ft.name, el.name);
          accParams[el.name] = defaultValue !== undefined ? defaultValue : el.default;
          return accParams;
        }, {});
      }
      return { name: ft.name, params };
    });
    this.__setPipelineStep(step.name, step.name, data, step.options);
  }

  __populateAutoMLParams(step) {
    const getDisableAutoML = (paramsAutoML) => {
      return _.isUndefined(this.isAutoMLOptimization) ? paramsAutoML : !this.isAutoMLOptimization;
    };
    return {
      ...step.params,
      disable_automl: getDisableAutoML(step.params.disable_automl),
    };
  }

  __populateStepData(step) {
    switch (step.type) {
      case PIPELINE_STEP_TYPES.QUERY:
        this.__populateQuery(step);
        break;
      case PIPELINE_STEP_TYPES.FEATURE_GENERATOR:
        this.__populateFeatureGenerator(step);
        break;
      case PIPELINE_STEP_TYPES.FEATURE_SELECTOR:
        this.__populateFeatureSelector(step);
        break;
      case PIPELINE_STEP_TYPES.AUTOML_PARAMS:
        //
        break;
      default:
        this.__populateTransform(step);
        break;
    }
  }

  getPipelineStepData() {
    DEFAULT_STEPS.forEach((step) => {
      this.__populateStepData(step);
    });
    return this.pipelineSteps;
  }

  getPipelineTVOStepData() {
    DEFAULT_STEPS.filter((step) => TVO_LIST.includes(step.type)).forEach((step) => {
      this.__populateStepData(step);
    });
    return this.pipelineSteps;
  }

  getQueryStepData() {
    const stepQuery = DEFAULT_STEPS.find((step) => step.type === PIPELINE_STEP_TYPES.QUERY);
    return this.__populateQuery(stepQuery);
  }

  getAutoMLStep() {
    const step = DEFAULT_STEPS[0];
    return {
      name: step.name,
      customName: step.name,
      options: step.options,
      data: this.__populateAutoMLParams(step),
    };
  }
}

export default PipelineDataBuilderDefault;
