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

import random

import numpy as np
import torch
from library.classifiers.classifier import Classifier
from numpy import dtype
from pandas import DataFrame
from torch import nn, optim
from torch.autograd import Variable


class ScalingError(Exception):
    pass


class NoFeaturesError(Exception):
    pass


class LNN(Classifier):
    def __init__(self, save_model_parameters, config=None):

        super(LNN, self).__init__(
            save_model_parameters=save_model_parameters, config=config
        )

    def preprocess(self, num_cols, data):
        """Assumes input dataframe has already been sorted into {features,
        label, groupby} columns and tests that feature columns have been scaled for .
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

            data[data.columns[0:num_cols]] -= 127

        except AssertionError:
            raise ScalingError(
                "Tree Ensemble Classifier can only be trained with integers between 0 and 255. Please select a feature scaler or quantizer and add it to your pipeline."
            )
        except ValueError:
            raise NoFeaturesError(
                "There are no features for training. Check the preceding pipeline steps and make sure there are some features for modeling."
            )
        return data

    def initialize_lnn(self, num_inputs, num_outputs, num_hidden_layer):

        n_in, n_h, n_out = num_inputs, num_hidden_layer, num_outputs
        self._model = nn.Sequential(
            nn.Linear(n_in, n_h), nn.ReLU(), nn.Linear(n_h, n_out), nn.Sigmoid()
        )

        self._num_inputs = num_inputs
        self._num_outputs = num_outputs
        self._num_hidden_layer = num_hidden_layer

    def load_model(self, model_parameters):

        self.initialize_lnn(
            model_parameters["num_inputs"],
            model_parameters["num_outputs"],
            model_parameters["hidden_layer"],
        )

        state_dict = {}
        for item, value in model_parameters["model_state_dict"].items():
            state_dict[item] = torch.tensor(value)

        self._model.load_state_dict(state_dict)
        self._model_parameters = model_parameters

    def dump_model(self):

        model = {}

        state_dict = {}
        for item, value in self._model.state_dict().items():
            state_dict[item] = value.tolist()

        model["model_state_dict"] = state_dict
        model["num_inputs"] = self._num_inputs
        model["num_outputs"] = self._num_outputs
        model["hidden_layer"] = self._num_hidden_layer

        return model

    def recognize_vectors(
        self, vectors_to_recognize, model_parameters=None, include_predictions=False
    ):

        if model_parameters is not None:
            self.load_model(model_parameters)

        for index, feature_vector in enumerate(vectors_to_recognize):

            # shift categories by 1
            tfeature_vector = torch.from_numpy(
                np.array(feature_vector["Vector"])
            ).float()
            y_pred = self.predict(tfeature_vector) + 1

            vectors_to_recognize[index]["CategoryVector"] = int(y_pred)
            vectors_to_recognize[index]["DistanceVector"] = [0]

        return self._compute_classification_statistics(
            range(1, self._num_outputs + 1),
            vectors_to_recognize,
            include_predictions=include_predictions,
        )

    def predict(self, feature_vector):

        x = Variable(feature_vector, requires_grad=False)
        output = self._model.forward(x)

        print(output)

        return output.argmax()

    def train(self, loss, optimizer, x_val, y_val):
        x = Variable(x_val, requires_grad=False)
        y = Variable(y_val, requires_grad=False)

        # Reset gradient
        optimizer.zero_grad()

        # Forward
        fx = self._model.forward(x)
        output = loss.forward(fx, y)

        # Backward
        output.backward()

        # Update parameters
        optimizer.step()

        return output.item()

    def fit(self, xtrain, ytrue, iterations=100, learning_rate=0.01, batch_size=25):

        indexes = list(range(xtrain.shape[0]))
        random.shuffle(indexes)

        torch.manual_seed(42)
        trX = torch.from_numpy(xtrain.values).float()
        trY = torch.from_numpy(ytrue.values - 1).long()

        n_examples, _ = trX.size()
        loss = torch.nn.CrossEntropyLoss()
        optimizer = optim.Adam(self._model.parameters(), lr=learning_rate)

        costs = []
        for i in range(iterations):
            cost = 0.0
            num_batches = n_examples // batch_size
            for k in range(num_batches):
                start, end = k * batch_size, (k + 1) * batch_size
                cost += self.train(loss, optimizer, trX[start:end], trY[start:end])

            print("Epoch %d, cost = %f" % (i + 1, cost / num_batches))

            costs.append(cost / num_batches)

        return costs
