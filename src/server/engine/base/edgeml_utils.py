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

import os

import numpy as np
import scipy.cluster
import scipy.spatial

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf


def medianHeuristic(data, projectionDimension, numPrototypes, W_init=None):
    """
    This method can be used to estimate gamma for ProtoNN. An approximation to
    median heuristic is used here.
    1. First the data is collapsed into the projectionDimension by W_init. If
    W_init is not provided, it is initialized from a random normal(0, 1). Hence
    data normalization is essential.
    2. Prototype are computed by running a  k-means clustering on the projected
    data.
    3. The median distance is then estimated by calculating median distance
    between prototypes and projected data points.
    data needs to be [-1, numFeats]
    If using this method to initialize gamma, please use the W and B as well.
    TODO: Return estimate of Z (prototype labels) based on cluster centroids
    andand labels
    TODO: Clustering fails due to singularity error if projecting upwards
    W [dxd_cap]
    B [d_cap, m]
    returns gamma, W, B
    """
    assert data.ndim == 2
    X = data
    featDim = data.shape[1]
    if projectionDimension > featDim:
        print("Warning: Projection dimension > feature dimension. Gamma")
        print("\t estimation due to median heuristic could fail.")
        print("\tTo retain the projection dataDimension, provide")
        print("\ta value for gamma.")

    if W_init is None:
        W_init = np.random.normal(size=[featDim, projectionDimension])
    W = W_init
    XW = np.matmul(X, W)
    assert XW.shape[1] == projectionDimension
    assert XW.shape[0] == len(X)
    # Requires [N x d_cap] data matrix of N observations of d_cap-dimension and
    # the number of centroids m. Returns, [n x d_cap] centroids and
    # elementwise center information.
    B, centers = scipy.cluster.vq.kmeans2(XW, numPrototypes)
    # Requires two matrices. Number of observations x dimension of observation
    # space. Distances[i,j] is the distance between XW[i] and B[j]
    distances = scipy.spatial.distance.cdist(XW, B, metric="euclidean")
    distances = np.reshape(distances, [-1])
    gamma = np.median(distances)
    gamma = 1 / (2.5 * gamma)
    return gamma.astype("float32"), W.astype("float32"), B.T.astype("float32")


def multiClassHingeLoss(logits, label):
    """
    MultiClassHingeLoss to match C++ Version - No TF internal version
    """

    flatLogits = tf.reshape(logits, [-1])
    label_ = tf.argmax(input=label, axis=1, output_type=tf.dtypes.int32)

    correctId = tf.range(0, label.shape[0]) * label.shape[1] + label_
    correctLogit = tf.gather(flatLogits, correctId)

    maxLabel = tf.argmax(input=logits, axis=1, output_type=tf.dtypes.int32)
    top2, _ = tf.nn.top_k(logits, k=2, sorted=True)

    wrongMaxLogit = tf.where(tf.equal(maxLabel, label_), top2[:, 1], top2[:, 0])

    return tf.reduce_mean(input_tensor=tf.nn.relu(1.0 + wrongMaxLogit - correctLogit))


def crossEntropyLoss(logits, label):
    """
    Cross Entropy loss for MultiClass case in joint training for
    faster convergence
    """
    return tf.reduce_mean(
        input_tensor=tf.nn.softmax_cross_entropy_with_logits(
            logits=logits, labels=tf.stop_gradient(label)
        )
    )


def mean_absolute_error(logits, label):
    """
    Function to compute the mean absolute error.
    """
    return tf.reduce_mean(input_tensor=tf.abs(tf.subtract(logits, label)))


def hardThreshold(A, s):
    """
    Hard thresholding function on Tensor A with sparsity s
    """
    A_ = np.copy(A)
    A_ = A_.ravel()
    if len(A_) > 0:
        th = np.percentile(np.abs(A_), (1 - s) * 100.0, interpolation="higher")
        A_[np.abs(A_) < th] = 0.0
    A_ = A_.reshape(A.shape)
    return A_


def updateSource(src, dest):
    """
    zero out entries in dest that are zeros in src tensor
    """

    indices = tf.constant(np.argwhere(src == 0))
    updates = tf.constant([0 for _ in range(len(indices))], dtype=tf.dtypes.float32)
    dest.scatter_nd_update(indices, updates)


def countnnZ(A, s, bytesPerVar=4):
    """
    Returns # of non-zeros and representative size of the tensor
    Uses dense for s >= 0.5 - 4 byte
    Else uses sparse - 8 byte
    """
    params = 1
    hasSparse = False
    for i in range(0, len(A.shape)):
        params *= int(A.shape[i])
    if s < 0.5:
        nnZ = np.ceil(params * s)
        hasSparse = True
        return nnZ, nnZ * 2 * bytesPerVar, hasSparse
    else:
        nnZ = params
        return nnZ, nnZ * bytesPerVar, hasSparse


def getPrecisionRecall(cmatrix, label=1):
    trueP = cmatrix[label][label]
    denom = np.sum(cmatrix, axis=0)[label]
    if denom == 0:
        denom = 1
    recall = trueP / denom
    denom = np.sum(cmatrix, axis=1)[label]
    if denom == 0:
        denom = 1
    precision = trueP / denom
    return precision, recall


def getMacroPrecisionRecall(cmatrix):
    # TP + FP
    precisionlist = np.sum(cmatrix, axis=1)
    # TP + FN
    recalllist = np.sum(cmatrix, axis=0)
    precisionlist__ = [
        cmatrix[i][i] / x if x != 0 else 0 for i, x in enumerate(precisionlist)
    ]
    recalllist__ = [
        cmatrix[i][i] / x if x != 0 else 0 for i, x in enumerate(recalllist)
    ]
    precision = np.sum(precisionlist__)
    precision /= len(precisionlist__)
    recall = np.sum(recalllist__)
    recall /= len(recalllist__)
    return precision, recall


def getMicroPrecisionRecall(cmatrix):
    # TP + FP
    precisionlist = np.sum(cmatrix, axis=1)
    # TP + FN
    recalllist = np.sum(cmatrix, axis=0)
    num = 0.0
    for i in range(len(cmatrix)):
        num += cmatrix[i][i]

    precision = num / np.sum(precisionlist)
    recall = num / np.sum(recalllist)
    return precision, recall


def getMacroMicroFScore(cmatrix):
    """
    Returns macro and micro f-scores.
    Refer: http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.104.8244&rep=rep1&type=pdf
    """
    precisionlist = np.sum(cmatrix, axis=1)
    recalllist = np.sum(cmatrix, axis=0)
    precisionlist__ = [
        cmatrix[i][i] / x if x != 0 else 0 for i, x in enumerate(precisionlist)
    ]
    recalllist__ = [
        cmatrix[i][i] / x if x != 0 else 0 for i, x in enumerate(recalllist)
    ]
    macro = 0.0
    for i in range(len(precisionlist)):
        denom = precisionlist__[i] + recalllist__[i]
        numer = precisionlist__[i] * recalllist__[i] * 2
        if denom == 0:
            denom = 1
        macro += numer / denom
    macro /= len(precisionlist)

    num = 0.0
    for i in range(len(precisionlist)):
        num += cmatrix[i][i]

    denom1 = np.sum(precisionlist)
    denom2 = np.sum(recalllist)
    pi = num / denom1
    rho = num / denom2
    denom = pi + rho
    if denom == 0:
        denom = 1
    micro = 2 * pi * rho / denom
    return macro, micro


def restructreMatrixBonsaiSeeDot(A, nClasses, nNodes):
    """
    Restructures a matrix from [nNodes*nClasses, Proj] to
    [nClasses*nNodes, Proj] for SeeDot
    """
    tempMatrix = np.zeros(A.shape)
    rowIndex = 0

    for i in range(0, nClasses):
        for j in range(0, nNodes):
            tempMatrix[rowIndex] = A[j * nClasses + i]
            rowIndex += 1

    return tempMatrix


def preProcessData(train, test, isRegression=False):
    """
    Function to pre-process input data
    Expects a .npy file of form [lbl feats] for each datapoint
    Outputs a train and test set datapoints appended with 1 for Bias induction
    dataDimension, numClasses are inferred directly
    """
    dataDimension = int(train.shape[1]) - 1

    Xtrain = train[:, 0:dataDimension]
    Ytrain_ = train[:, -1]

    Xtest = test[:, 0:dataDimension]
    Ytest_ = test[:, -1]

    # Mean Var Normalisation
    mean = np.mean(Xtrain, 0)
    std = np.std(Xtrain, 0)
    std[std[:] < 0.000001] = 1
    Xtrain = (Xtrain - mean) / std
    Xtest = (Xtest - mean) / std
    # End Mean Var normalisation

    # Classification.
    if not isRegression:
        numClasses = max(Ytrain_) - min(Ytrain_) + 1
        numClasses = int(max(numClasses, max(Ytest_) - min(Ytest_) + 1))

        lab = Ytrain_.astype("uint8")
        lab = np.array(lab) - min(lab)

        lab_ = np.zeros((Ytrain_.shape[0], numClasses))
        lab_[np.arange(Ytrain_.shape[0]), lab] = 1
        if numClasses == 2:
            Ytrain = np.reshape(lab, [-1, 1])
        else:
            Ytrain = lab_

        lab = Ytest_.astype("uint8")
        lab = np.array(lab) - min(lab)

        lab_ = np.zeros((Ytest_.shape[0], numClasses))
        lab_[np.arange(Ytest_.shape[0]), lab] = 1
        if numClasses == 2:
            Ytest = np.reshape(lab, [-1, 1])
        else:
            Ytest = lab_

    elif isRegression:
        # The number of classes is always 1, for regression.
        numClasses = 1
        Ytrain = Ytrain_
        Ytest = Ytest_

    trainBias = np.ones([Xtrain.shape[0], 1])
    Xtrain = np.append(Xtrain, trainBias, axis=1)
    testBias = np.ones([Xtest.shape[0], 1])
    Xtest = np.append(Xtest, testBias, axis=1)

    mean = np.append(mean, np.array([0]))
    std = np.append(std, np.array([1]))

    if isRegression == False:
        return dataDimension + 1, numClasses, Xtrain, Ytrain, Xtest, Ytest, mean, std
    elif isRegression == True:
        return (
            dataDimension + 1,
            numClasses,
            Xtrain,
            Ytrain.reshape((-1, 1)),
            Xtest,
            Ytest.reshape((-1, 1)),
            mean,
            std,
        )
