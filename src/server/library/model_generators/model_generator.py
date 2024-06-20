"""
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
"""

import logging

import engine.base.utils as utils
from engine.base.utils import clean_results
from library.classifiers.classifier import Classifier
from library.model_validation.validation_method import ValidationMethod
from logger.log_handler import LogHandler
from numpy import array

logger = LogHandler(logging.getLogger(__name__))


class ModelGeneratorError(Exception):
    pass


class ModelGenerator(object):
    """Base class for model generators."""

    def __init__(
        self,
        config,
        classifier,
        validation_method,
        team_id,
        project_id,
        pipeline_id,
        save_model_parameters=True,
        **kwargs
    ):
        assert isinstance(classifier, Classifier)
        assert isinstance(validation_method, ValidationMethod)

        self._config = config
        self._classifier = classifier
        self._validation_method = validation_method
        self.team_id = team_id
        self.pipeline_id = pipeline_id
        self.project_id = project_id

        # Populate from the config dictionary, use defaults
        self.sort_data = config.get("sort_data", 0)
        self.number_of_features = len(self._validation_method.feature_columns)
        self.number_of_folds = config.get("number_of_folds", 5)
        self.ranking_metric = config.get("ranking_metric", "f1_score")
        self.best_scores = []
        self.class_map = config.get("class_map")
        self.save_model_parameters = save_model_parameters

        self.results = {"models": {}, "metrics": {}}

    def get_results(self):
        return clean_results(self.results)

    def _initialize_validation_method(self):
        self._validation_method.preprocess_data(self._classifier)

        # Prep the configuration parameters
        random_state = self._config.get("random_state")

        return self._validation_method.generate_validation(random_state=random_state)

    def _get_model_results_template(self):
        return {
            "parameters": {},
            "metrics": {"validation": {}, "train": {}, "test": {}},
            "training_metrics": {},
            "validation_set": [],
            "train_set": [],
            "test_set": [],
            "debug": {},
            "feature_statistics": {"validation": {}, "train": {}, "test": {}},
        }

    def _package(self, data):
        vector_list = []
        for index, _ in enumerate(data):
            item_ints = [i for i in data[index][:-1]]

            if self._config.get("estimator_type", "classification") == "regression":
                category = data[index][-1]
            else:
                category = int((data[index][-1]))
            pkg_dict = {
                "Category": category,
                "CategoryVector": [],
                "DistanceVector": [],
                "Vector": list(item_ints),
            }
            vector_list.append(pkg_dict)

        return vector_list

    def _package_model_parameters(self, **kwards):
        """pacakge model parameters after training so they are in a serializable state
        after this they should be able to be stored in the database as a json as well as
        loaded by the classifier"""

    def _write(self, model_parameters):
        """writes a model to the classifier

        Args:
            model parameters (dict): should be the output of pacakge_model_parameters"""

        self._classifier.load_model(model_parameters)

    def _test(self, data):
        """recognizes a set of feature vectors using a loaded model on the hardware"""
        test_data = array(data)

        reco_vector_list = self._package(test_data)

        stats = self._classifier.recognize_vectors(reco_vector_list)

        return stats

    def _train(self, train_data, validate_data=None, test_data=None):
        """train a model usinging a specific algorithm

        Args:
            train_data; data used to train the model
            validate_data: data used for model validation during training

        Returns:
            dict: A json serializabled version of the model parameters
            dict: the training metrics ie. loss, training  accuracy across epochs or iterations.

        """

    def _store_model_data(
        self,
        key,
        parameters,
        model_result_template=None,
        training_metrics=None,
    ):
        if model_result_template is None:
            model_result_template = self._get_model_results_template()

        # Validate and store results
        self.results["models"][key] = model_result_template

        self.results["models"][key]["classifier_costs"] = self._classifier.compute_cost(
            parameters
        )

        if self.save_model_parameters:
            self.results["models"][key]["parameters"] = parameters

        self.results["models"][key]["model_size"] = self.results["models"][key][
            "classifier_costs"
        ]["flash"]

        self.results["models"][key]["training_metrics"] = training_metrics

    def _get_classification_and_metrics(
        self, key, validate_data=None, train_data=None, test_data=None
    ):
        # Validate and store results

        if train_data is not None and train_data.shape[0] > 0:
            self.results["models"][key]["metrics"]["train"] = self._test(train_data)
            self.results["models"][key]["feature_statistics"][
                "train"
            ] = compute_feature_stats(train_data)

        if validate_data is not None and validate_data.shape[0] > 0:
            self.results["models"][key]["metrics"]["validation"] = self._test(
                validate_data
            )
            self.results["models"][key]["feature_statistics"][
                "validation"
            ] = compute_feature_stats(validate_data)

        if test_data is not None and test_data.shape[0] > 0:
            self.results["models"][key]["metrics"]["test"] = self._test(test_data)
            self.results["models"][key]["feature_statistics"][
                "test"
            ] = compute_feature_stats(test_data)

    def run(self):
        """calls the algorithm, runs validation, stores results"""

        self._initialize_validation_method()

        # Generate models and collect results
        for fold in range(self._validation_method.number_of_sets):
            (
                train_data,
                validate_data,
                test_data,
            ) = self._validation_method.next_validation()
            fold_name = (
                self._validation_method.name if self._validation_method.name else fold
            )
            key = "Fold {0}".format(fold_name)

            # Run the traning algorithm
            model_parameters, training_metrics = self._train(
                train_data, validate_data=validate_data, test_data=test_data
            )

            # store the model data
            self._store_model_data(
                key,
                parameters=model_parameters,
                training_metrics=training_metrics,
            )

            # set the model as the current loadable model
            self._write(model_parameters)

            # get the metrics for the train, test and validate data sets for this model
            self._get_classification_and_metrics(
                key,
                train_data=train_data,
                validate_data=validate_data,
                test_data=test_data,
            )

        test_results = [
            (
                key,
                self.results["models"][key]["metrics"]["test"][self.ranking_metric][
                    "average"
                ],
            )
            for key, value in self.results["models"].items()
            if self.results["models"][key]["metrics"]["test"]
        ]

        self.best_scores = sorted(test_results, key=lambda x: x[1], reverse=True)

        #        # Return the neurons from the highest-scoring model
        #        if self.best_scores:
        #            recommended_key = self.best_scores[0][0]
        #        else:
        #            recommended_key = list(self.results["models"].keys())[0]

        #        if self.save_model_parameters:
        #            self.results["neurons"] = self.results["models"][recommended_key][
        #                "parameters"
        #            ]

        result_matrix = utils.get_metric_matrix(self.results, defaults={"model": 0})

        aggregate_metrics = utils.get_metric_matrix_stats(
            result_matrix, group_columns=["model"]
        ).drop("model", axis=1)

        self.results["metrics"] = aggregate_metrics.to_dict("records")


def compute_outliers(d):
    outliers = {}
    for feature in d.columns:
        outliers[feature] = (
            d[d[feature] < d[feature].quantile(0.045)][feature].values.tolist()[:2]
            + d[d[feature] > d[feature].quantile(0.955)][feature].values.tolist()[:2]
        )
    return outliers


def compute_feature_stats(df):
    g = df.groupby(df.columns[-1])

    M = {}
    for k, v in g.groups.items():
        M[k] = (
            g.get_group(k)[df.columns[:-1]]
            .describe(percentiles=[0.045, 0.25, 0.5, 0.75, 0.955])
            .round(2)
            .to_dict()
        )
        outliers = compute_outliers(g.get_group(k)[df.columns[:-1]])
        for feature in M[k].keys():
            M[k][feature]["median"] = g.get_group(k)[df.columns[:-1]][feature].median()
            M[k][feature]["outlier"] = outliers[feature]

    l = {k: {} for k in M[next(iter(M))].keys()}

    for label, features in M.items():
        for feature, stats in features.items():
            l[feature][label] = stats

    return l
