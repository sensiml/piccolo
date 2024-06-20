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

from __future__ import print_function

import logging
import os

import engine.base.edgeml_utils as utils
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from library.model_generators.model_generator import ModelGenerator
from library.optimizers.edgeml_bonsai import EdgemlBonsai
from library.optimizers.edgeml_bonsai_trainer import EdgemlBonsaiTrainer

logger = logging.getLogger(__name__)


class TrainBonsai(ModelGenerator):
    """ """

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
        super(TrainBonsai, self).__init__(
            config,
            classifier,
            validation_method,
            team_id,
            project_id,
            pipeline_id,
            save_model_parameters,
        )

        self._params = {
            "projection_dimension": config.get("projection_dimension", 10),
            "tree_depth": config.get("tree_depth", 3),
            "sigma": config.get("sigma", 1),
            "epochs": config.get("epochs", 100),
            "reg_W": config.get("reg_W", 0.001),
            "reg_V": config.get("reg_v", 0.001),
            "reg_Theta": config.get("reg_Theta", 0.001),
            "reg_Z": config.get("reg_Z", 0.0001),
            "sparse_W": config.get("sparse_W", 0.3),
            "sparse_V": config.get("sparse_V", 0.3),
            "sparse_Theta": config.get("sparse_Theta", 0.62),
            "sparse_Z": config.get("sparse_Z", 0.2),
            "batch_size": config.get("batch_size", 1),
            "random_state": config.get("random_sate", 43),
            "learning_rate": config.get("learning_rate", 0.001),
        }

    def _package_model_parameters(self, model, mean, variance):

        results = {
            "V": flatten_matrix(model.V),
            "W": flatten_matrix(model.W),
            "Z": flatten_matrix(model.Z),
            "T": flatten_matrix(model.T),
            "Mean": mean,
            "Variance": variance,
            "projection_dimension": int(self._params["projection_dimension"]),
            "tree_depth": int(self._params["tree_depth"]),
            "sigma": float(self._params["sigma"]),
            "num_nodes": model.totalNodes,
            "num_classes": model.numClasses,
            "num_features": model.dataDimension,
        }

        # seeDotDir = '/home/cknorow/SeeDot/'
        # np.savetxt(seeDotDir + "Mean", mean)
        # np.savetxt(seeDotDir + "Std", variance)

        return results

    def _train(self, train_data, validate_data=None, test_data=None):

        # Fixing seeds for reproducibility
        # tf.compat.v1.set_random_seed(self._params["random_state"])
        np.random.seed(self._params["random_state"])

        (
            dataDimension,
            numClasses,
            Xtrain,
            Ytrain,
            Xtest,
            Ytest,
            mean,
            std,
        ) = utils.preProcessData(train_data.values, validate_data.values, False)

        if numClasses > 2:
            sparW = 0.2
            sparV = 0.2
            sparT = 0.2
        else:
            sparW = 15
            sparV = 1
            sparT = 1

        if self._params["sparse_W"]:
            sparW = self._params["sparse_W"]
        if self._params["sparse_V"]:
            sparV = self._params["sparse_V"]
        if self._params["sparse_Theta"]:
            sparT = self._params["sparse_Theta"]

        sparZ = self._params["sparse_Z"]

        if self._params["batch_size"] is None:
            batchSize = np.maximum(100, int(np.ceil(np.sqrt(Ytrain.shape[0]))))
        else:
            batchSize = self._params["batch_size"]

        useMCHLoss = True
        if numClasses == 2:
            numClasses = 1
            useMCHLoss = False

        # numClasses = 1 for binary case
        bonsaiObj = EdgemlBonsai(
            numClasses,
            dataDimension,
            self._params["projection_dimension"],
            self._params["tree_depth"],
            self._params["sigma"],
            isRegression=False,
        )

        bonsaiTrainer = EdgemlBonsaiTrainer(
            bonsaiObj,
            lW=self._params["reg_W"],
            lT=self._params["reg_Theta"],
            lV=self._params["reg_V"],
            lZ=self._params["reg_Z"],
            sW=sparW,
            sT=sparT,
            sV=sparV,
            sZ=sparZ,
            learningRate=self._params["learning_rate"],
            useMCHLoss=useMCHLoss,
            pipeline_id=self.pipeline_id,
        )

        training_metrics = bonsaiTrainer.fit(
            batchSize,
            self._params["epochs"],
            Xtrain.astype(np.float32),
            Xtest.astype(np.float32),
            Ytrain.astype(np.float32),
            Ytest.astype(np.float32),
        )
        model_parameters = self._package_model_parameters(bonsaiObj, mean, std)

        return model_parameters, training_metrics


def flatten_matrix(numpy_array):
    """Flatten a numpy array and convert it to a serializable format"""

    M = []
    for i in range(numpy_array.shape[0]):
        for j in range(numpy_array.shape[1]):
            M.append(float(numpy_array[i][j]))

    return M


def flatten_transpose_multi_matrix(numpy_array, num_nodes, num_classes):
    """Translates the tf matrix to optimal format for bonsai classifier
    Both V and W matricies need to be decomposed into their
    individual node matricies and transposed. We do the transpose
    here, so that on the device it is a simple multiplication
    """

    M = []
    for node in range(num_nodes):
        tmp_v = np.transpose(numpy_array[node * num_classes : (node + 1) * num_classes])
        for i in range(tmp_v.shape[0]):
            for j in range(tmp_v.shape[1]):
                M.append(float(tmp_v[i][j]))

    return M


def restructure_matrix(A, num_nodes, num_classes):
    """
    Restructures a matrix from [nNodes*nClasses, Proj] to
    [nClasses*nNodes, Proj] for SeeDot
    """
    return flatten_matrix(A)

    tmp_A = np.zeros(A.shape)
    row_index = 0

    for i in range(0, num_classes):
        for j in range(0, num_nodes):
            tmp_A[row_index] = A[j * num_classes + i]
            row_index += 1

    return flatten_matrix(tmp_A)
