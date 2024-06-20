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

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import binascii

try:
    import tensorflow as tf
except:
    print("Tensorflow is not installed!")

""" This is an Experimental API Library Subject to Change


Example useage for train test split

rand_max = 1
max_frequency_bin=num_cols
num_steps=row_size
min_noise=-10
max_noise=10
mask_value=127
batch_size =32

data  = tf.data.Dataset.from_tensor_slices((x_train, y_train))
noise_ds = data.map(lambda image, label: tf_add_image_noise(image, label, rand_max, min_noise, max_noise))
freq_ds = noise_ds.map(lambda image, label: tf_mask_image_row(image, label, rand_max, max_frequency_bin, mask_value))
masked_ds = freq_ds.map(lambda image, label: tf_mask_image_column(image, label, num_steps, rand_max, max_frequency_bin, mask_value))
shuffle_aug = masked_ds.shuffle(buffer_size=x_train.shape[0], reshuffle_each_iteration=True).batch(batch_size)
shuffle_ds = data.shuffle(buffer_size=x_train.shape[0], reshuffle_each_iteration=True).batch(batch_size)

 """


def convert_tf_lite(tflite_model):
    return binascii.hexlify(tflite_model).decode("ascii")


def visualize_features(
    event_index, x_train, y_train, row_size, num_cols, class_map=None, figsize=(16, 8)
):
    if class_map:
        reverse_class_map = {int(v): k for k, v in class_map.items()}
        print("Class: ", reverse_class_map[np.argmax(y_train[event_index])])
    else:
        print("Class: ", np.argmax(y_train[event_index]))
    fig, axs = plt.subplots(1, 2, figsize=figsize)
    sns.heatmap(x_train[event_index].reshape(row_size, num_cols).T, ax=axs[0])
    plt.plot(x_train[event_index].reshape(row_size, num_cols))
    plt.ylim((0, 256))
    plt.show()


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


def visualize_tf_data(data, index, row_size, num_cols):
    count = 0
    for image, label in data.take(index):
        count += 1
        if count == index:
            fig = plt.figure(figsize=(row_size + 2, 4))
            sns.heatmap(image.numpy().reshape(-1, num_cols).T)
            plt.title(f"Label: {np.argmax(label)}")
            plt.show()


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


def plot_training_results(
    tf_model,
    history,
    x_train,
    y_train,
    x_validate,
    y_validate,
    class_map=None,
    figsize=(32, 10),
):
    fig, axs = plt.subplots(2, 2, figsize=figsize)
    epochs = range(1, len(history["loss"]) + 1)
    axs[0][0].plot(epochs, history["loss"], "g.", label="Training los    s")
    axs[0][0].plot(epochs, history["val_loss"], "b", label="Validation loss")
    axs[0][0].set_title("Training and validation loss")
    axs[0][0].set_xlabel("Epochs")
    axs[0][0].set_ylabel("Loss")
    axs[1][0].plot(epochs, history["accuracy"], "g.", label="Training Accuracy")
    axs[1][0].plot(epochs, history["val_accuracy"], "b", label="Validation Accuracy")
    axs[1][0].set_title("Training and validation Accuracy")
    axs[1][0].set_xlabel("Epochs")
    axs[1][0].set_ylabel("Accuracy")

    sns.heatmap(
        tf.math.confusion_matrix(
            np.argmax(tf_model.predict(x_train), axis=1), np.argmax(y_train, axis=1)
        ),
        annot=True,
        ax=axs[0][1],
    )

    axs[0][1].set_title("Training Confusion Matrix")

    sns.heatmap(
        tf.math.confusion_matrix(
            np.argmax(tf_model.predict(x_validate), axis=1),
            np.argmax(y_validate, axis=1),
        ),
        annot=True,
        ax=axs[1][1],
    )

    axs[1][1].set_title("Validation Confusion Matrix")

    plt.show()


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
