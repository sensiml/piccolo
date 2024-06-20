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

from abc import abstractmethod

from engine.base.calculate_statistics import StatsCalc
from numpy import dtype
from pandas import DataFrame
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
)

# A classifier is part of the train-validate-optimize step, working alongside
# model-generator and validation-method objects.
# a classifier is/should be responsible for the feature-recognition process.


class ScalingError(Exception):
    pass


class ClassifierError(Exception):
    pass


class NoFeaturesError(Exception):
    pass


class Classifier(object):
    """
    A base class for classifier objects.
    """

    def __init__(self, save_model_parameters=True, config=None):
        self._config = config
        self._model = None
        self.model_parameters = None
        self.save_model_paramters = save_model_parameters

    @abstractmethod
    def preprocess(self, num_cols, data, **kwargs):
        """Assumes input dataframe has already been sorted into {features,
        label, groupby} columns and tests that feature columns have been scaled for PME.
        :param data: an input dataframe, with at least num_cols
        :param num_cols: the number of columns to test are in range (0, 255)
        :return: the unchanged dataframe, if all tests pass
        """
        integer_dtypes = [
            dtype("int64"),
            dtype("int32"),
            dtype("int8"),
            dtype("int16"),
            dtype("uint64"),
            dtype("uint32"),
            dtype("uint8"),
            dtype("uint16"),
        ]
        try:
            # Attempt to cast floating point representations to integers
            data[data.columns[0:num_cols]] = data[data.columns[0:num_cols]].astype(int)
            assert isinstance(data, DataFrame)
            assert len(data.columns) >= num_cols
            assert data[data.columns[0:num_cols]].values.max() < 256
            assert data[data.columns[0:num_cols]].values.min() >= 0
            assert (
                data[data.columns[0:num_cols]]
                .apply(lambda c: c.dtype)
                .isin(integer_dtypes)
                .all()
            )
        except AssertionError:
            raise ScalingError(
                "Classifier can only be trained with integers between 0 and 255. Please select a feature scaler or quantizer and add it to your pipeline."
            )
        except ValueError:
            raise NoFeaturesError(
                "There are no features for training PME. Please check the preceding pipeline steps and make sure there are some features for modeling."
            )
        return data

    def load_model(self, model_parameters):
        """load a trained model intot he classfier"""

    def recognize_vectors(
        self, vectors_to_recognize, model_parameters=None, include_predictions=False
    ):
        """recognize multiple feature vectors"""

    def compute_cost(self, model_parameters):
        """compute the total bytes for this classifier"""
        return 0

    def _compute_classification_statistics(
        self, categories, recognized_vectors, include_predictions=False
    ):
        unknown = 0
        properclass = 0
        improperclass = 0
        actual_category_counts = {}
        recognized_category_counts = {}  # based only on the first element in vector
        confusion_matrix = {}
        temp = {}
        all_cats = set()

        # Create a confusion matrix
        for v in categories:
            all_cats.add(int(v))
        for v in recognized_vectors:
            all_cats.add(int(v["CategoryVector"]))

        # To avoid to create doubled UNK column
        if 0 in all_cats:
            all_cats.remove(0)

        # remove the 0 from the all_cats
        all_cats = sorted(all_cats)

        for v in all_cats:
            temp[v] = 0
        temp["UNC"] = 0
        temp["UNK"] = 0
        for v in all_cats:
            confusion_matrix[v] = dict(temp)

        for v in recognized_vectors:
            if v["CategoryVector"] == 0:
                # Report unknowns
                unknown = unknown + 1
                confusion_matrix[int(v["Category"])]["UNK"] += 1
            else:
                confusion_matrix[int(v["Category"])][v["CategoryVector"]] += 1
                if v["CategoryVector"] == int(v["Category"]):
                    properclass += 1
                else:
                    improperclass += 1

            if v["Category"] in actual_category_counts:
                actual_category_counts[v["Category"]] = (
                    actual_category_counts[v["Category"]] + 1
                )
            else:
                actual_category_counts[v["Category"]] = 1

            # These metrics are not too important yet, but might need to be updated for multiple firing neurons
            if v["CategoryVector"] in recognized_category_counts:
                recognized_category_counts[v["CategoryVector"]] = (
                    recognized_category_counts[v["CategoryVector"]] + 1
                )
            else:
                recognized_category_counts[v["CategoryVector"]] = 1

        # Gather truth and prediction values from recognized vectors
        y_true = [int(x["Category"]) for x in recognized_vectors]
        y_pred = [int(x["CategoryVector"]) for x in recognized_vectors]

        # Calculate statistics from confusion matrix and y_true, y_pred

        if self._config:
            class_map = self._config.get("class_map", None)
        else:
            class_map = None

        stats_obj = StatsCalc(
            y_true,
            y_pred,
            confusion_matrix,
            class_map=class_map,
        )
        stats_obj.calc_all_metrics()
        statistics = {
            "UnknownPercent": 100 * float(unknown) / float(len(recognized_vectors)),
            "ProperClassificationPercent": 100
            * float(properclass)
            / float(len(recognized_vectors)),
            "ImproperClassificationPercent": 100
            * float(improperclass)
            / float(len(recognized_vectors)),
            "VectorInTestSet": len(recognized_vectors),
            # assumption is that they are all the same size
            "FeaturesPerVector": len(recognized_vectors[0]["Vector"]),
            "ActualCategoryCounts": actual_category_counts,
            "RecognizedCategoryCounts": recognized_category_counts,
            "ConfusionMatrix": confusion_matrix,
            "accuracy": stats_obj.accuracy if len(set(y_true)) > 1 else None,
            "sensitivity": stats_obj.sensitivity if len(set(y_true)) > 1 else None,
            "positive_predictive_rate": stats_obj.positive_predictive_rate
            if len(set(y_true)) > 1
            else None,
            "f1_score": stats_obj.f1_score if len(set(y_true)) > 1 else None,
            "precision": stats_obj.precision if len(set(y_true)) > 1 else None,
            "specificity": None,
            "y_true": None,
            "y_pred": None,
        }  # stats_obj.specificity if len(set(y_true)) > 1 else None}

        if include_predictions:
            distance_vector = None
            if "DistanceVector" in recognized_vectors[0]:
                distance_vector = [x["DistanceVector"] for x in recognized_vectors]

            statistics.update(
                {
                    "y_true": y_true,
                    "y_pred": y_pred,
                    "DistanceVector": distance_vector,
                }
            )

        return statistics

    def _compute_regression_statistics(self, recognized_vectors):
        # Gather truth and prediction values from recognized vectors
        y_true = [x["Category"] for x in recognized_vectors]
        y_pred = [x["CategoryVector"] for x in recognized_vectors]

        statistics = {
            # assumption is that they are all the same size
            "y_true": y_true,
            "y_pred": y_pred,
            "mean_squared_error": {"average": mean_squared_error(y_true, y_pred)},
            "mean_absolute_error": {"average": mean_absolute_error(y_true, y_pred)},
            "median_absolute_error": {"average": median_absolute_error(y_true, y_pred)},
        }

        return statistics
