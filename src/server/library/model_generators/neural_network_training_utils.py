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

import binascii
import copy
import os
import random

import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf


def augment_with_auxiliary_unknown(
    ix_aux_unknown,
    ix_aux_unknown_kw,
    size_aux_unknown_kw,
    size_aux_unknown,
):

    ix_aux_unknown_kw_selected = ix_aux_unknown_kw
    ix_aux_unknown_selected = ix_aux_unknown

    if len(ix_aux_unknown_kw) > 0 and size_aux_unknown_kw > 0:
        ix_aux_unknown_kw_selected = ix_aux_unknown_kw[
            np.random.choice(
                range(len(ix_aux_unknown_kw)),
                size=size_aux_unknown_kw,
                replace=(len(ix_aux_unknown_kw) < size_aux_unknown_kw),
            )
        ]

    if len(ix_aux_unknown) > 0 and size_aux_unknown > 0:
        ix_aux_unknown_selected = ix_aux_unknown[
            np.random.choice(
                range(len(ix_aux_unknown)),
                size=size_aux_unknown,
                replace=(len(ix_aux_unknown) < size_aux_unknown),
            )
        ]

    return np.concatenate((ix_aux_unknown_kw_selected, ix_aux_unknown_selected))


def augment_feature_with_unknown(
    ix_fv_unknown,
    ix_fv_keywords,
    ix_aux_unknown,
    ix_aux_unknown_kw,
    size_input_unknown: int = 0,
    size_aux_unknown_kw: int = 0,
    size_aux_unknown: int = 0,
    min_aug_unknown_size: int = 1000,
):
    """augmenting the feature DataFrame with Unknown labels from an auxiliary feature table

    Args:
        ix_fv_unknown (numpy array): indices of featres labeled as unknown
        ix_fv_keywords (numpy array): indices of featres labeled as keyword
        ix_aux_unknown (numpy array): indices of auxiliary featres labeled as unknown
        ix_aux_unknown_kw (numpy array): indices of auxiliary featres labeled as keyword
        size_input_unknown (1000, int): number of target labels randomly taken from the input table
        size_aux_unknown_kw (500, int): number of non-target labels randomly taken from the auxiliary table
        size_aux_unknown (500, int): number of target labels randomly taken from the auxiliary table
        min_aug_unknown_size (1000, int) minimum size of augmentation for input unknowns

    Returns:
        DataFrame: the augmented feature table
    """

    if size_input_unknown <= 0:
        size_input_unknown = max(
            [min_aug_unknown_size, len(ix_fv_keywords), len(ix_fv_unknown)]
        )

    ix_fv_unknown = ix_fv_unknown[
        np.random.choice(
            range(len(ix_fv_unknown)),
            size=size_input_unknown,
            replace=(len(ix_fv_unknown) < size_input_unknown),
        )
    ]

    if size_aux_unknown_kw <= 0:
        size_aux_unknown_kw = max(5000, size_input_unknown)
    if size_aux_unknown <= 0:
        size_aux_unknown = max(5000, size_input_unknown)

    # augmenting with auxiliary unknown data
    ix_aux = augment_with_auxiliary_unknown(
        ix_aux_unknown,
        ix_aux_unknown_kw,
        size_aux_unknown_kw,
        size_aux_unknown,
    )

    # merging all components
    ix_fv = np.concatenate((ix_fv_keywords, ix_fv_unknown))

    return ix_fv, ix_aux


def get_data_aux_indices(train_data, auxiliary_fv, class_map):
    """returning the indices of keywords and unknown

    Args:
        train_data (DataFrame): training feature vectors
        auxiliary_fv (DataFrame): auxiliary feature vectors used for data augmentation
        class_map (dict): keys are class names and values are integer class codes

    Returns:
        ix_fv_keywords (arr, int32): indices of keyword data features
        ix_fv_unknown (arr, int32): indices of unknown data features
        ix_aux_unknown_kw (arr, int32): indices of auxiliary features representing a keyword (not necessarily the same as the project target keywords)
        ix_aux_unknown (arr, int32): indices of auxiliary unknown features
    """

    feature_columns = train_data.columns
    unknown_code = class_map["Unknown"]

    kw_list = [kw.lower() for kw in set(auxiliary_fv["Label"].values)]

    exclude_list = []  # exclude keywords that are already in the dataset
    for key, value in class_map.items():
        if key.lower() in kw_list:
            exclude_list.append(key.lower())

    ix_aux = np.asarray(list(range(auxiliary_fv.shape[0])), dtype=np.int32)

    ix_aux_unknown_kw = ix_aux[
        auxiliary_fv["Label"].apply(
            lambda x: False if x.lower() in exclude_list else True
        )
    ]

    ix_aux_unknown = ix_aux[auxiliary_fv["Label"] == "Unknown"]

    ix_fv = np.asarray(list(range(train_data.shape[0])), dtype=np.int32)

    # 1 keywords provided by user
    ix_fv_keywords = ix_fv[train_data[feature_columns[-1]] != unknown_code]

    # 2 unknowns provided by user resampled
    ix_fv_unknown = ix_fv[train_data[feature_columns[-1]] == unknown_code]

    return ix_fv_keywords, ix_fv_unknown, ix_aux_unknown_kw, ix_aux_unknown


def add_sparse_random_noise(
    X,
    max_change: int = 5,
    bias_range: "tuple[int, int]" = (-8, 8),
    fraction: float = 0.1,
):
    """adding random noise to randomly chosen pixels of a subset of the input vectors

    Args:
        X (array): numpy 2D array representing the feature table
        max_change (5, int): maximum number of pixels in each selected vector to be changed
        bias_range ((-8, 8), tuple): the bias interval bounding the random noise
        fraction (0.1, float): ranges between 0 and 1, fraction of the input vectors to be modified

    """

    N = X.shape[0]
    n = int(N * fraction)
    nR = X.shape[1]
    nC = X.shape[2]

    for j in np.random.choice(range(N), size=n, replace=False):

        n_change = np.random.randint(0, max_change + 1)

        for _ in range(n_change):

            R = np.random.randint(nR)
            C = np.random.randint(nC)
            noise = np.random.randint(bias_range[0], bias_range[1], size=1)
            X[j, R, C, 0] += noise

    X[X > 127] = 127
    X[X < -127] = -127

    return X


def add_column_row_random_noise(
    X,
    max_change: int = 5,
    bias_range: "tuple[int, int]" = (-8, 8),
    fraction: float = 0.1,
):
    """randomly changing columns and/or rows by adding a constant bias along the column/row"""

    N = X.shape[0]
    n = int(N * fraction)
    nR = X.shape[1]
    nC = X.shape[2]

    for j in np.random.choice(range(N), size=n, replace=False):

        n_change = np.random.randint(0, max_change + 1)

        for _ in range(n_change):

            randint = np.random.randint(2)

            if randint == 0:  # changing a column
                R = np.random.randint(nR)
                noise = np.random.randint(bias_range[0], bias_range[1], size=nC)
                X[j, R, :, 0] += noise
            else:  # changing a row
                C = np.random.randint(nC)
                noise = np.random.randint(bias_range[0], bias_range[1], size=nR)
                X[j, :, C, 0] += noise

    X[X > 127] = 127
    X[X < -127] = -127

    return X


def mask_image(
    X,
    max_change: int = 5,
    mask_value: "tuple[int, int]" = (-5, 5),
    fraction: float = 0.1,
    mode="row",
):
    """masking out a rows/columns by values randomly taken from the mask_value range"""

    N = X.shape[0]
    n = int(N * fraction)
    nR = X.shape[1]
    nC = X.shape[2]

    for j in np.random.choice(range(N), size=n, replace=False):

        n_change = np.random.randint(0, max_change + 1)

        for _ in range(n_change):

            if mode == "row":  # changing a column
                R = np.random.randint(nR)
                mask = np.random.randint(mask_value[0], mask_value[1])
                X[j, R, :, 0] = mask
            elif mode == "column":  # changing a row
                C = np.random.randint(nC)
                mask = np.random.randint(mask_value[0], mask_value[1])
                X[j, :, C, 0] = mask
            else:
                pass

    return X


def alter_feature_data(
    X_input,
    sparse_noise=False,
    bias_noise=False,
    row=False,
    column=False,
    seed=None,
    fraction=0.3,
):
    """Changing the input feature array to facilitate data augmentation and to avoid over-fitting."""

    X = copy.deepcopy(X_input)

    # Note: This function has been designed and tested to alter the 2D spectral features,
    # such as spectrograms, MFE, MFCC, etc., and X_input is of shape (None, n_row, n_column, 1)
    if len(X.shape) != 4:
        return X

    if seed is None:  # choose a seed randomly
        np.random.seed(random.randint(0, 1000))

    if sparse_noise:
        X = add_sparse_random_noise(
            X, max_change=128, bias_range=(-10, 10), fraction=fraction
        )

    if bias_noise:
        X = add_column_row_random_noise(
            X, max_change=16, bias_range=(-10, 10), fraction=fraction
        )

    if row:
        X = mask_image(
            X, max_change=8, mask_value=(-127, 127), fraction=fraction, mode="row"
        )

    if column:
        X = mask_image(
            X, max_change=8, mask_value=(-127, 127), fraction=fraction, mode="column"
        )

    return X


def get_label_stat(y_train):

    labels = np.asarray([np.argmax(y) for y in y_train])
    label_set = set(labels)
    n_labels = [len((np.where(labels == i)[0])) for i in label_set]

    return n_labels, min(n_labels), max(n_labels)


def resample(y_train, method="oversample", n_sample=None):

    labels = np.asarray([np.argmax(y) for y in y_train])
    label_set = set(labels)
    n_labels = [len((np.where(labels == i)[0])) for i in label_set]

    # temporarily handling the empty inputs
    if len(label_set) == 0:
        return np.asarray(list(range(y_train.shape[0])), dtype=np.int32)

    if not n_sample is None and isinstance(n_sample, int) and n_sample > 0:
        pass
    elif method == "undersample":
        n_sample = min(n_labels)
    elif method == "median":
        n_sample = int(np.median(n_labels))
    elif method == "mean":
        n_sample = int(np.mean(n_labels))
    else:
        n_sample = max(n_labels)

    first = True
    for lbl in label_set:

        idx = np.random.choice(np.where(labels == lbl)[0], size=n_sample, replace=True)
        if first:
            selected_indices = idx
            first = False
        else:
            selected_indices = np.concatenate((selected_indices, idx))

    return selected_indices


def get_one_hot(targets, nb_classes):
    res = np.eye(nb_classes)[np.array(targets).reshape(-1)]
    return res.reshape(list(targets.shape) + [nb_classes])


def features_to_tensor_convert(train_data, class_map):
    num_classes = len(class_map)

    y_labels = train_data.iloc[:, -1]  # .apply(lambda x: class_map[x])

    y_values_encoded = get_one_hot(y_labels.values - 1, num_classes)

    y_values_encoded = y_values_encoded.reshape(y_labels.shape[0], num_classes)

    x_values = train_data.iloc[:, :-1].values

    return x_values, y_values_encoded


def reshape_input_data_to_model(data, tf_model):

    tf_model_shape = tuple([-1] + (list(tf_model.input_shape)[1:]))

    try:
        reshaped_data = data.reshape(tf_model_shape)
    except:
        raise Exception(
            f"Input shape of training data {data.shape} doesn't match the input shape of this model {tf_model_shape} ."
        )

    return reshaped_data


def convert_to_tensorflow_data_loader(x_train, y_train, batch_size, tf_model):

    x_train_reshaped = reshape_input_data_to_model(x_train, tf_model)

    data = tf.data.Dataset.from_tensor_slices((x_train_reshaped, y_train))

    """

    TODO: add augmentation steps to training

    rand_max = 1
    min_noise = -10
    max_noise = 10
    mask_value = 127


    noise_ds = data.map(
        lambda image, label: add_image_noise(
            image, label, rand_max, min_noise, max_noise
        )
    )

    freq_ds = noise_ds.map(
        lambda image, label: mask_image_row(
            image, label, rand_max, num_cols, mask_value
        )
    )

    masked_ds = freq_ds.map(
        lambda image, label: mask_image_column(
            image, label, row_size, rand_max, num_cols, mask_value
        )
    )

    shuffle_aug = masked_ds.shuffle(
        buffer_size=x_train.shape[0], reshuffle_each_iteration=True
    ).batch(batch_size)

    """
    # TODO: Set a max buffer size instead of always using the entire dataset

    shuffle_ds = data.shuffle(
        buffer_size=x_train.shape[0], reshuffle_each_iteration=True
    ).batch(batch_size)

    return shuffle_ds


def reset_weights(model):
    for layer in model.layers:
        if isinstance(layer, tf.keras.Model):  #
            reset_weights(layer)
            continue
        if hasattr(layer, "cell"):
            init_container = layer.cell
        else:
            init_container = layer

        for key, initializer in init_container.__dict__.items():
            if "initializer" not in key:
                continue

            if key == "recurrent_initializer":
                var = getattr(init_container, "recurrent_kernel")
            else:
                var = getattr(init_container, key.replace("_initializer", ""))

            var.assign(initializer(var.shape, var.dtype))
            # use the initializer


def encode_tflite(tflite_model):
    return binascii.hexlify(tflite_model).decode("ascii")


def decode_tflite(model_parameters):
    return binascii.unhexlify(model_parameters["tflite"].encode("ascii"))
