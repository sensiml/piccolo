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

from library.model_generators.model_generator import ModelGenerator
from numpy import array
from sklearn.linear_model import LinearRegression


class TrainLinearRegressionOLS(ModelGenerator):
    """Creates optimal order-agnostic training set and trains with the resulting vector."""

    def __init__(
        self,
        config,
        classifier,
        validation_method,
        team_id,
        project_id,
        pipeline_id,
        save_model_parameters,
    ):
        """Initialize with defaults for missing values."""
        super(TrainLinearRegressionOLS, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self._params = {
            "fit_intercept": config.get("fit_intercept", True),
            "positive": config.get("positive", False),
        }

    def _package_model_parameters(self, model):
        """convert a  linear regression to a json serializable form that can be
        saved and used to create a model for our linear_regression.c function"""

        model_data = {}
        model_data["coefficients"] = model.coef_
        model_data["intercept"] = model.intercept_
        model_data["n_features_in"] = model.n_features_in_
        model_data["num_coefficients"] = len(model.coef_)

        return model_data

    def _test(self, data):
        """Package set of vectors for the simulator and recognize the tensors returns the stats of the recogntion"""
        test_data = array(data)
        reco_vector_list = self._package(test_data)

        return self._classifier.recognize_vectors(reco_vector_list)

    def _train(self, train_data, validate_data=None, test_data=None):
        reg = LinearRegression(**self._params)
        label = self._config.get("label_column")

        X_q = train_data[[x for x in train_data.columns if x != label]]
        y = train_data[label]

        reg.fit(X_q, y)

        return self._package_model_parameters(reg), None
