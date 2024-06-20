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
const QUERY = "Query";
const INPUT_DATA = "Input Data";
const TRANSFORM = "Transform";
const SEGMENTER = "Segmenter";
const AUGMENTATION = "Augmentation";
const FEATURE_GENERATOR = "Feature Generator";
const SAMPLER = "Sampler";
const FEATURE_SELECTOR = "Feature Selector";
const CLASSIFIER = "Classifier";
const TRAINING_ALGORITHM = "Training Algorithm";
const VALIDATION = "Validation Method";
const AUTOML_PARAMS = "AUTOML_PARAMS";
const MODEL_SETTINGS = "Model Settings";

export const AUTOML_PARAMS_NAME = "Pipeline Settings";
export const PARENT_KEY = "Parent";

export const PIPELINE_STEP_TYPES = {
  QUERY,
  INPUT_DATA,
  TRANSFORM,
  SEGMENTER,
  AUGMENTATION,
  FEATURE_GENERATOR,
  SAMPLER,
  FEATURE_SELECTOR,
  CLASSIFIER,
  TRAINING_ALGORITHM,
  VALIDATION,
  AUTOML_PARAMS,
  MODEL_SETTINGS,
};

export const DEFAULT_CLASSIFIER = "PME";

export const AUTOML_STEP = {
  name: "Pipeline Settings",
  customName: "Pipeline Settings",
  nextSteps: null,
  mandatory: true,
  type: PIPELINE_STEP_TYPES.AUTOML_PARAMS,
  subtype: [],
  transformList: [],
  excludeTransform: [],
  data: {},
  limit: 1,
  set: false,
};

export const TRANSFORM_TYPES = {
  FEATURE_TRANSFORM: "Feature Transform",
  SENSOR_TRANSFORM: "Sensor Transform",
  SEGMENT_TRANSFORM: "Segment Transform",
  SENSOR_FILTER: "Sensor Filter",
  AUGMENTATION: "Augmentation",
};

export const TRANSFORM_LIST = [
  PIPELINE_STEP_TYPES.TRANSFORM,
  PIPELINE_STEP_TYPES.SEGMENTER,
  PIPELINE_STEP_TYPES.SAMPLER,
];

export const TVO_LIST = [
  PIPELINE_STEP_TYPES.CLASSIFIER,
  PIPELINE_STEP_TYPES.TRAINING_ALGORITHM,
  PIPELINE_STEP_TYPES.VALIDATION,
];

export const DISABLED_CLASSIFIERS = ["TF Micro"];

export const ONETIME_ADDED = [FEATURE_GENERATOR, FEATURE_SELECTOR];

export const DISABLED_STEPS = [INPUT_DATA];

export const DISABLED_FOR_AUTOML_STEPS = [CLASSIFIER, TRAINING_ALGORITHM];

export const DISABLED_FOR_CUSTOM_STEPS = [AUTOML_PARAMS];

export const AUTOML = "auto";
export const AUTO_ML_V2 = "automlv2";
export const EXECUTION_TYPES = {
  AUTOML,
  AUTO_ML_V2,
};

// params

export const TVO_PARAM = "tvo";
export const SELECTOR_SET_PARAM = "selectorset";
export const DISABLE_AUTOML_SELECTION_PARAM_NAME = "disable_automl";

export const AUTOML_SEARCHED_STEPS = {
  TVO_PARAM,
  SELECTOR_SET_PARAM,
};

export const AUTOML_SEARCHED_STEPS_TYPES_LOOKUP = [
  { stepType: TRAINING_ALGORITHM, paramName: TVO_PARAM },
  { stepType: CLASSIFIER, paramName: TVO_PARAM },
  { stepType: FEATURE_SELECTOR, paramName: SELECTOR_SET_PARAM },
];

export const AUTOML_SEARCHED_STEPS_TYPES = {
  [TVO_PARAM]: TRAINING_ALGORITHM,
  [TVO_PARAM]: CLASSIFIER,
  // [SELECTOR_SET_PARAM]: FEATURE_SELECTOR,
};

export const AUTOML_PARAM_GROUPS = {
  AUTOML_OPTIMIZATION: "General Settings",
  TATGET_CONTRAINTS: "Optimization Targets",
  AUTOML_SEARCH_SETTING: "Search Settings",
};

// IDs to add

export const SEGMENTER_ID_PARAM = "SegmentID";

export const DISABLED_TRAINING_ALGO = [];

// execution_type

export const PIPELINE_GROUPS = {
  PEPROCESSING: {
    name: "Preprocessing",
    type: "preprocessing",
  },
  FEATURE_EXTRACOR: {
    name: "Feature Extraction",
    type: "feature_extractor",
  },
  TVO: {
    name: "Model Training",
    type: "tvo",
  },
};

export const PIPELINE_STEP_DESCRIPTIONS = {
  "Sensor Transform": {
    descpription:
      "Act on a single sample of sensor data directly as a pre-processing step. Can create a new source that is fed as input to the next step in the pipeline. ie Ax,Ay,Az can become MagnitudeAxAyAz.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/sensor-transforms.html",
  },
  "Sensor Filter": {
    descpription:
      "Modifies a sensor in place and performs some sort of filtering (ie. moving average). This acts on a Sensor source that was either input or created using a sensor transform. This does not create a new source.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/sensor-filters.html",
  },
  Segmenter: {
    descpription:
      "Takes input from the sensor transform/filter step and buffers the data until a segment is found.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/segmenters.html",
  },
  "Segment Transform": {
    descpription:
      "Perform manipulations on an entire segment of data. Segment transforms modify the data in place, so if you use a segment transform be aware that your data will be modified.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/segment-transforms.html",
  },
  "Feature Generator": {
    descpription:
      "A collection of feature generators work on a segment of data to extract meaningful information. The combination of the output from all feature generators becomes a feature vector",
    docLink: "https://sensiml.com/documentation/pipeline-functions/feature-generators.html",
  },
  "Feature Transform": {
    descpription:
      "Perform row wise operations on a single feature vector. The most common feature transform in the pipeline is Min Max Scale, which translates the output of the feature generation step into 1byte feature values.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/feature-generators.html",
  },
  Classifier: {
    descpription:
      "Takes a feature vector as an input and returns a classification based on a pre-defined model.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/classifiers.html",
  },
  "Feature Selector": {
    descpription: "Used to optimally select a subset of features before training a Classifier.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/feature-selectors.html",
  },
  Samplers: {
    descpription:
      "Used to remove outliers and noisy data before classification. Samplers are useful in improving the robustness of the model.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/samplers.html",
  },
  Augmentation: {
    descpription:
      "Large number of model parameters or insufficient amounts of data might cause an over-fitting problem. One solution to address this problem is using data augmentation which is a process to generate more data by using existing data.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/augmentations.html",
  },
  "Training Algorithm": {
    descpription: "Training algorithms are used to select the optimal parameters of a model.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/training-algorithms.html",
  },
  Validation: {
    descpription:
      "Validation methods are used to check the robustness and accuracy of a model and diagnose if a model is overfitting or underfitting.",
    docLink: "https://sensiml.com/documentation/pipeline-functions/validation-algorithms.html",
  },
  "Feature Quantization": {
    descpription:
      "Normalize and scale data to integer values between min_bound and max_bound, while leaving specified passthrough columns unscaled. This operates on each feature column separately and saves min/max data for the knowledge pack to use for recognition of new feature vectors.",
    docLink:
      "https://sensiml.com/documentation/pipeline-functions/feature-transforms.html?highlight=min%20max%20scale",
  },
  "Pipeline Settings": {
    descpription: `AutoML is used to create a set of models within the desired statistical (accuracy, f1-score, sensitivity, etc.) and classifier size (neurons, features) parameters. As the algorithm iterates each optimization step, it narrow downs the searching space to find a desired number of models. The optimization terminates when the desired model is found or the number of iterations reaches the max number of iterations. We take advantage of dynamic programming and optimizations for training algorithms to speed up the computation. This makes it possible to search large parameter spaces quickly and efficiently. The results are ranked by the fitness score which takes into account the model’s statistical and hardware parameters.`,
    docLink: "https://sensiml.com/documentation/analytics-studio-notebook/sensiml-automl.html",
  },
};
