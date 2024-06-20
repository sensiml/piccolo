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

import pandas as pd
from pandas import DataFrame
from os.path import dirname
from os.path import join
import numpy as np
from typing import Optional


class ClassLabelException(Exception):
    pass


class DataSets:
    def __init__(self):
        pass

    def load_activity_raw(self) -> DataFrame:
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, "data", "activity_raw.csv"))

    def load_activity_raw_toy(self) -> DataFrame:
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, "data", "activity_raw_toy.csv"))

    def load_activity_norm(self) -> DataFrame:
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, "data", "activity_norm.csv"))

    def load_activity_quant(self) -> DataFrame:
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, "data", "activity_quant.csv"))

    def load_activity_quant_toy(self) -> DataFrame:
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, "data", "activity_quant_toy.csv"))

    def load_gesture_raw(self) -> DataFrame:
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, "data", "gesture_raw.csv"))

    def load_toy_data(self) -> DataFrame:
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, "data", "toy_data.csv"))

    @staticmethod
    def generate_step_data(
        window_size: int = 100,
        num_classes: int = 5,
        num_iterations: int = 2,
        scale_factor: int = 100,
        noise_scale: int = 5,
        class_labels: Optional[list] = None,
        class_values: Optional[list] = None,
        loop: bool = False,
    ):
        """Generate a labeled test data vector.

        Args:
            window_size (int, optional): The size of each segment window.
            num_classes (int, optional): The number of separate classes
            num_iterations (int, optional): The number of iterations to create.
            scale_factor (int, optional): scale the values of the data by this much before adding noise
            noise_scale (int, optional): The range of noise to add (-noise_scale:noise_scale)
            class_labels (None, optional): you can pass specific class labels as an array, otherwise defaults to
             the range(num_classes)
            loop (bool, False): if True starts from class 1 at end of iteration. if False, starts at class num_classes and reverses at end of iteration

        Returns:
            DataFrame: a test data vector for building and testing models
        """
        class_labels = check_class_label(num_classes, class_labels)
        class_values = check_class_values(num_classes, class_values)
        delta = window_size * num_classes
        signal_length = num_iterations * delta

        y = np.zeros(signal_length)
        y_label = np.zeros(signal_length)

        for j in range(num_iterations):
            y_temp = np.zeros(window_size * num_classes)
            if j % 2 == 0:
                for i in range(num_classes):

                    y_temp[window_size * i : window_size * (i + 1)] = class_values[i]
                    y_label[
                        window_size * i + j * delta : window_size * (i + 1) + j * delta
                    ] = class_labels[i]
            else:
                for i in range(num_classes):
                    index = -1 - i
                    class_index = num_classes + index
                    if loop:
                        index = i
                        class_index = index
                    y_temp[window_size * i : window_size * (i + 1)] = class_values[
                        index
                    ]
                    y_label[
                        window_size * i + j * delta : window_size * (i + 1) + j * delta
                    ] = class_labels[class_index]
            y[delta * j : delta * (j + 1)] = y_temp * scale_factor

        if noise_scale > 0:
            y += np.array(
                [
                    np.random.choice(range(-noise_scale, noise_scale))
                    for i in range(len(y))
                ]
            )

        return pd.DataFrame({"Data": y.astype(np.int16), "Label": y_label.astype(int)})

    @staticmethod
    def generate_harmonic_data(
        window_size: int = 100,
        num_classes: int = 5,
        num_iterations: int = 2,
        scale_factor: int = 100,
        noise_scale: int = 5,
        class_labels: Optional[list] = None,
        harmonic_nodes: Optional[list[int]] = None,
    ):
        """Generate a labeled test data sin vector.

        Args:
            window_size (int, optional): The size of each segment window.
            num_classes (int, optional): The number of separate classes
            num_iterations (int, optional): The number of iterations to create.
            scale_factor (int, optional): scale the values of the data by this much before adding noise
            noise_scale (int, optional): The range of noise to add (-noise_scale:noise_scale)
            class_labels (None, optional): you can pass specific class labels as an array, otherwise defaults to
             the range(num_classes)

        Returns:
            DataFrame: a test data vector for building and testing models
        """

        class_labels = check_class_label(num_classes, class_labels)
        harmonic_nodes = check_class_values(num_classes, harmonic_nodes)

        delta = window_size * num_classes
        signal_length = num_iterations * delta

        y = np.zeros(signal_length)
        x = np.arange(signal_length)

        y_label = np.zeros(signal_length)
        for j in range(num_iterations):
            y_temp = np.zeros(delta)
            x = np.arange(window_size)
            if j % 2 == 0:
                for i in range(num_classes):
                    y_temp[window_size * i : window_size * (i + 1)] = get_standing_wave(
                        x, window_size, harmonic_nodes[i]
                    )
                    y_label[
                        window_size * i + j * delta : window_size * (i + 1) + j * delta
                    ] = class_labels[i]
            else:
                for i in range(num_classes):
                    y_temp[window_size * i : window_size * (i + 1)] = get_standing_wave(
                        x, window_size, harmonic_nodes[-1 - i]
                    )
                    y_label[
                        window_size * i + j * delta : window_size * (i + 1) + j * delta
                    ] = class_labels[num_classes - 1 - i]
            y[delta * j : delta * (j + 1)] = y_temp * scale_factor

        if noise_scale > 0:
            y += np.array(
                [
                    np.random.choice(range(-noise_scale, noise_scale))
                    for i in range(len(y))
                ]
            )

        return pd.DataFrame({"Data": y.astype(np.int16), "Label": y_label.astype(int)})


def get_standing_wave(x, L, n):
    ld = 2.0 * L / n
    return np.sin(x * (2 * np.pi) / ld)


def check_class_label(num_classes, class_labels=None):
    if class_labels is None:
        class_labels = range(1, num_classes + 1)
    elif len(class_labels) != num_classes:
        raise ClassLabelException(
            "The number of classes is not equal to the number of class labels."
        )

    for i in class_labels:
        if type(i) != type(1):
            raise ClassLabelException("class labels must be integers.")
    if i <= 0:
        raise ClassLabelException("class labels must be greater than zero.")

    return class_labels


def check_class_values(num_classes, class_values=None):
    if class_values is None:
        class_values = range(1, num_classes + 1)
    elif len(class_values) != num_classes:
        raise ClassLabelException(
            "The number of classes is not equal to the number of class values."
        )

    for i in class_values:
        if type(i) != type(1):
            raise ClassLabelException("class values must be type int")
        if i <= 0:
            raise ClassLabelException("class values must be greater than zero.")

    return class_values
