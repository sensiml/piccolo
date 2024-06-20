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

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import numpy as np
import tensorflow as tf


def mask_tensor_row(image, rand_max=1, max_frequency_bin=1, mask_value=127):
    for _ in range(np.random.randint(0, rand_max)):
        start = np.random.randint(0, max_frequency_bin)
        image_numpy = image.numpy()
        np.put(
            image_numpy, np.arange(start, image.shape[0], max_frequency_bin), mask_value
        )
        image = tf.constant(
            image_numpy, dtype=image.dtype, shape=image.shape, name="Const"
        )

    return image


def mask_tensor_columns(
    image, num_cols, rand_max=1, max_frequency_bin=1, mask_value=127
):
    num_masks = np.random.randint(0, rand_max)
    for _ in range(num_masks):
        start = np.random.randint(0, num_cols)
        image_numpy = image.numpy()
        np.put(
            image_numpy,
            np.arange(
                start * max_frequency_bin, start * max_frequency_bin + max_frequency_bin
            ),
            mask_value,
        )
        image = tf.constant(
            image_numpy, dtype=image.dtype, shape=image.shape, name="Const"
        )

    return image


def add_tensor_noise(image, rand_max=1, min_noise=-10, max_noise=10):
    if np.random.randint(0, rand_max):
        image_numpy = image.numpy()
        image = tf.constant(
            image_numpy + np.random.randint(min_noise, max_noise, size=image.shape),
            dtype=image.dtype,
            shape=image.shape,
            name="Const",
        )

    return image


def add_image_noise(
    image, label, rand_max=1, min_noise=10, max_noise=10, tf_int_type=tf.int32
):
    im_shape = image.shape
    [image] = tf.py_function(
        add_tensor_noise, [image, rand_max, min_noise, max_noise], [tf_int_type]
    )
    image.set_shape(im_shape)

    return image, label


def mask_image_row(
    image, label, rand_max=1, max_frequency_bin=1, mask_value=127, tf_int_type=tf.int32
):
    im_shape = image.shape
    [image] = tf.py_function(
        mask_tensor_row, [image, rand_max, max_frequency_bin, mask_value], [tf_int_type]
    )
    image.set_shape(im_shape)

    return image, label


def mask_image_column(
    image,
    label,
    num_cols,
    rand_max=1,
    max_frequency_bin=1,
    mask_value=127,
    tf_int_type=tf.int32,
):
    im_shape = image.shape
    [image] = tf.py_function(
        mask_tensor_columns,
        [image, num_cols, rand_max, max_frequency_bin, mask_value],
        [tf_int_type],
    )
    image.set_shape(im_shape)

    return image, label
