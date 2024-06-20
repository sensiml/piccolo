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
import _ from "lodash";
import { FORM_TYPES } from "consts";
import { PIPELINE_STEP_TYPES, AUTOML_PARAM_GROUPS as AutoMLParamGroups } from "store/autoML/const";
import { selectPipelineStedDataValues } from "store/containerBuildModel/selectors";

export const defaultAutoMLParams = {
  reset: true,
  iterations: 2,
  selectorset: true,
  tvo: true,
  hardware_target: {
    classifiers_sram: 3200,
  },
  population_size: 40,
  "prediction_target(%)": {
    f1_score: 100,
  },
  single_model: true,
  hierarchical_multi_model: false,
};

const AutoMLParams = [
  {
    name: "disable_automl",
    label: "Custom Training",
    default: false,
    type: FORM_TYPES.FORM_BOOLEAN_TYPE,
    group: AutoMLParamGroups.AUTOML_OPTIMIZATION,
    description:
      "By enabling custom training, you will be disabling the AutoML search. In this mode you can specify the hyperparameters for a single classifier and training algorithm. You will also be able to specify the feature selection algorithms used by the pipeline. The model performance will be evaluated using the selected validation method, but a single final model will be returned that is trained using all of the training data.",
  },
  {
    name: "prediction_target(%)",
    label: "Prediction_target(%)",
    group: AutoMLParamGroups.TATGET_CONTRAINTS,
    default: "f1_score",
    options: [
      { name: "f1-score", value: "f1_score" },
      { name: "Accuracy", value: "accuracy" },
      { name: "Sensitivity", value: "sensitivity" },
    ],
    type: FORM_TYPES.FORM_SELECT_TYPE,
    description:
      "Prediction targets are statistical scores of accuracy, f1_score and sensitivity. These scores are used to terminate the optimization process. If statistical targets (and hardware_targets) reach the desired scores, the optimization process is terminated for statistical optimization.",
    fieldset: [
      {
        parent: "prediction_target(%)",
        name: "f1_score",
        label: "f1-score",
        isFormHidden: true,
        type: FORM_TYPES.FORM_RANGE_INT_TYPE,
        default: 100,
        defaultStep: 1,
        range: [1, 100],
      },
      {
        parent: "prediction_target(%)",
        name: "accuracy",
        label: "Accuracy",
        isFormHidden: true,
        type: FORM_TYPES.FORM_RANGE_INT_TYPE,
        default: 100,
        defaultStep: 1,
        range: [1, 100],
      },
      {
        parent: "prediction_target(%)",
        name: "sensitivity",
        label: "Sensitivity",
        isFormHidden: true,
        type: FORM_TYPES.FORM_RANGE_INT_TYPE,
        default: 100,
        defaultStep: 1,
        range: [1, 100],
      },
    ],
  },
  {
    name: "hardware_target",
    label: "Hardware target",
    group: AutoMLParamGroups.TATGET_CONTRAINTS,
    default: "classifiers_sram",
    options: [
      { name: "Classifer Size(B)", value: "classifiers_sram" },
      // { name: "Latency", value: "latency" }
    ],
    type: FORM_TYPES.FORM_SELECT_TYPE,
    description:
      "Hardware_targets are latency, classifiers_sram. These scores are used to terminate the optimization process. If hardware targets reach the desired scores, the optimization process is terminated for hardware optimization.",
    fieldset: [
      {
        parent: "hardware_target",
        name: "classifiers_sram",
        label: "Classifer Size(B)",
        type: FORM_TYPES.FORM_INT_TYPE,
        default: 32 * 1000,
        defaultStep: 1000,
        range: [1, 1000 * 1000],
      },
      /*  {
        parent: "hardware_target",
        name: "latency",
        label: "Latency",
        type: FORM_TYPES.FORM_INT_TYPE,
        default: 100,
        defaultStep: 1,
        range: [1, 1000],
        },
      */
    ],
  },
  {
    name: "selectorset",
    label: "Optimize Feature Selector",
    group: AutoMLParamGroups.AUTOML_SEARCH_SETTING,
    default: true,
    opposite_value: "tvo",
    type: FORM_TYPES.FORM_BOOLEAN_TYPE,
    description: `The Feature Selector step will be optimized as part of the search space for the AutoML routine.`,
  },
  {
    name: "set_selectorset",
    label: "Select Feature Selector to optimize",
    group: AutoMLParamGroups.AUTOML_SEARCH_SETTING,
    description: `The Feature Selector step will be optimized as part of the search space for the AutoML routine.`,
    isShowIfParamName: "selectorset",
    options: [
      {
        name: "Information Gain",
        value: "Information Gain",
      },
      {
        name: "t-Test Feature Selector",
        value: "t-Test Feature Selector",
      },
      {
        name: "Univariate Selection",
        value: "Univariate Selection",
      },
      {
        name: "Tree-based Selection",
        value: "Tree-based Selection",
      },
    ],
    default: [
      "Information Gain",
      "t-Test Feature Selector",
      "Univariate Selection",
      "Tree-based Selection",
    ],
    type: FORM_TYPES.FORM_MULTI_SELECT_TYPE,
  },
  {
    name: "tvo",
    label: "Optimize training and classification Algorithms",
    group: AutoMLParamGroups.AUTOML_SEARCH_SETTING,
    opposite_value: "selectorset",
    default: true,
    type: FORM_TYPES.FORM_BOOLEAN_TYPE,
    description: `The machine learning training algorithm and classifier hyperparatemers will be optimized as part of the search space for the AutoML routine.`,
  },

  {
    name: "set_training_algorithm",
    label: "Select Training Algorithms to optimize",
    group: AutoMLParamGroups.AUTOML_SEARCH_SETTING,
    description: `The machine learning training algorithms will be optimized as part of the search space for the AutoML routine.`,
    isShowIfParamName: "tvo",
    options: [
      {
        name: "Hierarchical Clustering with Neuron Optimization​",
        value: "Hierarchical Clustering with Neuron Optimization",
      },
      {
        name: "RBF with Neuron Allocation Optimization",
        value: "RBF with Neuron Allocation Optimization",
      },
      {
        name: "Random Forest",
        value: "Random Forest",
      },
      {
        name: "xGBoost",
        value: "xGBoost",
      },
      {
        name: "Fully Connected Neural Network",
        value: "Train Fully Connected Neural Network",
      },
    ],
    default: [
      "Hierarchical Clustering with Neuron Optimization",
      "RBF with Neuron Allocation Optimization",
      "Random Forest",
      "xGBoost",
      "Train Fully Connected Neural Network",
    ],
    type: FORM_TYPES.FORM_MULTI_SELECT_TYPE,
  },

  {
    name: "iterations",
    label: "Iterations",
    group: AutoMLParamGroups.AUTOML_SEARCH_SETTING,
    range: [1, 15],
    defaultStep: 1,
    default: 1,
    type: FORM_TYPES.FORM_RANGE_INT_TYPE,
    description:
      "Defines the number of iterations the model will go through. At each iteration a new population of models is created by mutating the previous iterations population. A higher number of iteration produces better results but takes more time.",
  },
  {
    name: "population_size",
    label: "Population Size",
    group: AutoMLParamGroups.AUTOML_SEARCH_SETTING,
    default: 40,
    range: [10, 200],
    defaultStep: 10,
    type: FORM_TYPES.FORM_RANGE_INT_TYPE,
    description:
      "Defines how large the initial population is. A higher population means a larger initial search space is. A higher population typically produces better results but takes more time.",
  },
  {
    name: "allow_unknown",
    label: "Anomaly Detection",
    group: AutoMLParamGroups.AUTOML_SEARCH_SETTING,
    default: false,
    type: FORM_TYPES.FORM_BOOLEAN_TYPE,
    description:
      "Performs multiclass classification, but includes only classifiers that will predict Unknown (0) when presented with data outside the training distribution.",
  },
];

class StepDataAutoMLParameters {
  constructor({ state, type, subtype, id, selectedSteps }) {
    /* args: state, type, subtype */
    this.state = state;
    this.type = type;
    this.subtype = subtype;
    this.id = id;
    this.selectedSteps = selectedSteps;
  }

  // eslint-disable-next-line consistent-return
  __getInputContractFilterName() {
    if (this.type === PIPELINE_STEP_TYPES.TRAINING_ALGORITHM) {
      return this.INPUT_CLASSIFIERS;
    }
    if (this.type === PIPELINE_STEP_TYPES.VALIDATION) {
      return this.INPUT_VALIDATION_METHODS;
    }
  }

  __getSavedPipelineStepData() {
    if (!_.isEmpty(this.selectedSteps)) {
      return this.selectedSteps.find((step) => step.id === this.id)?.data;
    }
    return selectPipelineStedDataValues(this.state, this.id);
  }

  __getSavedParams(name, parent, defaultValue) {
    const defaultStepDataValues = this.__getSavedPipelineStepData();
    if (parent && defaultStepDataValues[parent] && defaultStepDataValues[parent][name]) {
      return defaultStepDataValues[parent][name];
    }
    if (defaultStepDataValues[name] && defaultStepDataValues[name]?.length) {
      return defaultStepDataValues[name];
    }
    if (defaultStepDataValues[name] && Object.keys(defaultStepDataValues[name])?.length) {
      return Object.keys(defaultStepDataValues[name]);
    }
    if (defaultStepDataValues && defaultStepDataValues[name] !== undefined) {
      return defaultStepDataValues[name];
    }
    return defaultValue;
  }

  getInputsData() {
    return AutoMLParams.map((param) => {
      let fieldset;
      if (param.fieldset?.length) {
        // transform fieldset
        fieldset = param.fieldset.map((fieldObj) => {
          return {
            ...fieldObj,
            default: this.__getSavedParams(fieldObj.name, fieldObj.parent, fieldObj.default),
          };
        });
      }
      return {
        // transform parm obj
        ...param,
        default: this.__getSavedParams(param.name, param.parent, param.default),
        fieldset,
      };
    });
  }

  getCardParams() {
    const value = this.__getSavedParams("disable_automl", null);

    return [
      {
        name: "disable_automl",
        tooltip: value
          ? "Run a specific training algorithm with user defined parameters."
          : "Performs a hyperparameter search over the parameters of the training algorithms, classifiers, and feature selectors.",
        label: "Training:",
        value: value ? "Custom" : "AutoML",
      },
    ];
  }

  getOutputData() {
    // eslint-disable-next-line no-console
    console.log("getDefaultInputsData");
  }
}

export default StepDataAutoMLParameters;
