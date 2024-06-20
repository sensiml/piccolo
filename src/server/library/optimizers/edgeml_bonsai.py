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

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.
from __future__ import print_function

import logging
import os
import warnings

import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))

PRINT_PROGRESS_LOGS = False


class EdgemlBonsai:
    def __init__(
        self,
        numClasses,
        dataDimension,
        projectionDimension,
        treeDepth,
        sigma,
        isRegression=False,
        W=None,
        T=None,
        V=None,
        Z=None,
    ):
        """
        Expected Dimensions:
        Bonsai Params // Optional
        W [numClasses*totalNodes, projectionDimension]
        V [numClasses*totalNodes, projectionDimension]
        Z [projectionDimension, dataDimension + 1]
        T [internalNodes, projectionDimension]
        internalNodes = 2**treeDepth - 1
        totalNodes = 2*internalNodes + 1
        sigma - tanh non-linearity
        sigmaI - Indicator function for node probabilities
        sigmaI - has to be set to infinity(1e9 for practicality)
        while doing testing/inference
        numClasses will be reset to 1 in binary case
        """
        self.dataDimension = dataDimension
        self.projectionDimension = projectionDimension
        self.isRegression = isRegression

        if (self.isRegression == True) & (numClasses != 1):
            warnings.warn("Number of classes cannot be greater than 1 for regression")
            self.numClasses = 1

        if numClasses == 2:
            self.numClasses = 1
        else:
            self.numClasses = numClasses

        self.treeDepth = treeDepth
        self.sigma = sigma

        self.internalNodes = 2 ** self.treeDepth - 1
        self.totalNodes = 2 * self.internalNodes + 1

        self.W = self.initW(W)
        self.V = self.initV(V)
        self.T = self.initT(T)
        self.Z = self.initZ(Z)

        self.assertInit()

        self.score = None
        self.X_ = None
        self.prediction = None

    def initZ(self, Z):
        if Z is None:
            Z = tf.Variable(
                tf.random.normal(shape=[self.projectionDimension, self.dataDimension])
            )
        else:
            Z = tf.Variable(tf.convert_to_tensor(Z, name="Z", dtype=tf.float32))

        return Z

    def initW(self, W):
        if W is None:
            W = tf.Variable(
                tf.random.normal(
                    [self.numClasses * self.totalNodes, self.projectionDimension]
                )
            )
        else:
            W = tf.Variable(tf.convert_to_tensor(W, name="W", dtype=tf.float32))
        return W

    def initV(self, V):
        if V is None:
            V = tf.Variable(
                tf.random.normal(
                    [self.numClasses * self.totalNodes, self.projectionDimension]
                )
            )
        else:
            V = tf.Variable(tf.convert_to_tensor(V, name="V", dtype=tf.float32))
        return V

    def initT(self, T):
        if T is None:
            T = tf.Variable(
                tf.random.normal([self.internalNodes, self.projectionDimension])
            )
        else:
            T = tf.Variable(tf.convert_to_tensor(T, name="T", dtype=tf.float32))
        return T

    def feedfoward(self, X, sigmaI):
        """
        Function to build the Bonsai Tree graph
        Expected Dimensions
        X is [_, self.dataDimension]
        """

        X_ = tf.divide(tf.matmul(self.Z, X, transpose_b=True), self.projectionDimension)

        W_ = self.W[0 : (self.numClasses)]
        V_ = self.V[0 : (self.numClasses)]

        self.__nodeProb = []
        self.__nodeProb.append(1)

        score_ = self.__nodeProb[0] * tf.multiply(
            tf.matmul(W_, X_), tf.tanh(self.sigma * tf.matmul(V_, X_))
        )
        for i in range(1, self.totalNodes):
            W_ = self.W[i * self.numClasses : ((i + 1) * self.numClasses)]
            V_ = self.V[i * self.numClasses : ((i + 1) * self.numClasses)]

            T_ = tf.reshape(
                self.T[int(np.ceil(i / 2.0) - 1.0)], [-1, self.projectionDimension]
            )

            prob = 1 + ((-1) ** (i + 1)) * tf.tanh(
                tf.multiply(np.float32(sigmaI), tf.matmul(T_, X_))
            )

            prob = tf.divide(prob, 2.0)
            prob = self.__nodeProb[int(np.ceil(i / 2.0) - 1.0)] * prob
            self.__nodeProb.append(prob)
            score_ += self.__nodeProb[i] * tf.multiply(
                tf.matmul(W_, X_), tf.tanh(self.sigma * tf.matmul(V_, X_))
            )

        self.score = score_
        self.X_ = X_
        return self.score, self.X_

    def getPrediction(self):
        """
        Takes in a score tensor and outputs a integer class for each data point
        """

        # Classification.
        if self.isRegression == False:
            if self.prediction is not None:
                return self.prediction

            if self.numClasses > 2:
                self.prediction = tf.argmax(input=tf.transpose(a=self.score), axis=1)
            else:
                self.prediction = tf.argmax(
                    input=tf.concat(
                        [tf.transpose(a=self.score), 0 * tf.transpose(a=self.score)], 1
                    ),
                    axis=1,
                )
        # Regression.
        elif self.isRegression == True:
            # For regression , scores are the actual predictions, just return them.
            self.prediction = self.score

        return self.prediction

    def assertInit(self):
        errmsg = "Number of Classes for regression can only be 1."
        if self.isRegression == True:
            assert self.numClasses == 1, errmsg
        errRank = "All Parameters must has only two dimensions shape = [a, b]"
        assert len(self.W.shape) == len(self.Z.shape), errRank
        assert len(self.W.shape) == len(self.T.shape), errRank
        assert len(self.W.shape) == 2, errRank
        msg = "W and V should be of same Dimensions"
        assert self.W.shape == self.V.shape, msg
        errW = "W and V are [numClasses*totalNodes, projectionDimension]"
        assert self.W.shape[0] == self.numClasses * self.totalNodes, errW
        assert self.W.shape[1] == self.projectionDimension, errW
        errZ = "Z is [projectionDimension, dataDimension]"
        assert self.Z.shape[0] == self.projectionDimension, errZ
        assert self.Z.shape[1] == self.dataDimension, errZ
        errT = "T is [internalNodes, projectionDimension]"
        assert self.T.shape[0] == self.internalNodes, errT
        assert self.T.shape[1] == self.projectionDimension, errT
        assert int(self.numClasses) > 0, "numClasses should be > 1"
        msg = "# of features in data should be > 0"
        assert int(self.dataDimension) > 0, msg
        msg = "Projection should be  > 0 dims"
        assert int(self.projectionDimension) > 0, msg
        msg = "treeDepth should be >= 0"
        assert int(self.treeDepth) >= 0, msg
