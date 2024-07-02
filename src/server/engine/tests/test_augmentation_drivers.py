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
import numpy as np
import pytest

from django.core.exceptions import ValidationError
from engine.drivers import (
    augmentation_driver,
)
from library.core_functions.augmentation import copy, is_augmented
from library.models import Transform
import gzip
import pickle

from library.core_functions.augmentation import (
    add_noise_contracts,
    scale_amplitude_contracts,
    time_stretch_contracts,
    pitch_shift_contracts,
    random_crop_contracts,
)


##########################################################
def load_datasegments(path):

    with gzip.open(path, "rb") as fid:
        data = pickle.load(fid)
    return data


@pytest.fixture
def input_data():
    return load_datasegments(
        os.path.join(os.path.dirname(__file__), "data", "audio_segments_4test.pkl")
    )


##########################################################

project_id = "1236ef6e-bbf4-11ed-afa1-0242ac120002"
pipeline_id = "ML"
team_id = "Tests"
user_id = "Test_user"
task_id = "Augmentation"

step = {
    "name": "augmentation_set",
    "type": "augmentationset",
    "inputs": {
        "label_column": "Labels",
        "group_columns": [
            "CaptureID",
            "Labels",
            "SegmentID",
            "segment_uuid",
            "Set",
        ],
        "passthrough_columns": [
            "CaptureID",
            "Labels",
            "SegmentID",
            "segment_uuid",
            "Set",
        ],
    },
    "outputs": ["temp.augmentation_set0.data_0"],
    "feature_table_value": None,
}


##########################################################
def run_augmentation_drive(input_data, step_set):

    step["set"] = step_set

    output_data, _ = augmentation_driver(
        input_data, step, team_id, project_id, pipeline_id, user_id, task_id
    )

    return output_data


@pytest.mark.django_db
def test_augmentation_add_noise(input_data):

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Add Noise",
        subtype="Supervised",
        input_contract=add_noise_contracts["input_contract"],
        output_contract=add_noise_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="add_noise",
    )

    ########################################
    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Add Noise",
                "inputs": {
                    "background_scale_range": [10, 100],
                    "fraction": 0.5,
                    "noise_types": ["white", "pink"],
                    "target_labels": ["knocking"],
                    "filter": {"Set": ["Train", "Validate"]},
                    "input_columns": ["channel_0"],
                },
            },
        ],
    )

    assert len(output_data) == len(input_data) + round(
        0.5
        * len(
            [
                d
                for d in input_data
                if d["metadata"]["Labels"] in ["knocking"]
                and d["metadata"]["Set"] in ["Train", "Validate"]
            ]
        )
    )

    ########################################
    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Add Noise",
                "inputs": {
                    "background_scale_range": [2, 20],
                    "fraction": 2,
                    "noise_types": ["white"],
                    "target_labels": ["knocking"],
                    "filter": {"Set": ["Train"]},
                    "input_columns": ["channel_0"],
                    "replace": True,
                },
            },
        ],
    )

    assert len(output_data) == round(
        2
        * len(  # augmented
            [
                d
                for d in input_data
                if d["metadata"]["Labels"] in ["knocking"]
                and d["metadata"]["Set"] in ["Train"]
            ]
        )
    ) + len(input_data)

    ######################################## output := input
    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Add Noise",
                "inputs": {
                    "background_scale_range": [0, 0],
                    "fraction": 1,
                    "noise_types": ["white"],
                    "filter": {"Set": ["Train"]},
                    "input_columns": ["channel_0"],
                    "replace": True,
                },
            },
        ],
    )

    assert len(output_data) == len(  # augmented
        [d for d in input_data if d["metadata"]["Set"] in ["Train"]]
    ) + len(input_data)

    in_segment = input_data[0]
    for out_segment in output_data:
        if (
            out_segment["metadata"]["segment_uuid"][:14]
            == in_segment["metadata"]["segment_uuid"][:14]
        ):
            break

    np.testing.assert_array_equal(in_segment["data"], out_segment["data"])


##########################################################


@pytest.mark.django_db
def test_augmentation_scale_amplitude(input_data):

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Scale Amplitude",
        subtype="Supervised",
        input_contract=scale_amplitude_contracts["input_contract"],
        output_contract=scale_amplitude_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="scale_amplitude",
    )

    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Scale Amplitude",
                "inputs": {
                    "scale_range": [0.1, 2],
                    "fraction": 0.5,
                    "target_labels": ["Click"],
                    "input_columns": ["channel_0"],
                },
            },
        ],
    )

    assert len(output_data) == len(input_data) + round(
        0.5 * len([d for d in input_data if d["metadata"]["Labels"] in ["Click"]])
    )

    ######################################## output :=  input
    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Scale Amplitude",
                "inputs": {
                    "scale_range": [2, 2],
                    "fraction": 1,
                    "target_labels": ["Click"],
                    "input_columns": ["channel_0"],
                    "replace": True,
                },
            },
        ],
    )

    # replacing the input data that meets the filter condition with
    # the augmented versions
    assert len(output_data) == len(  # augmented
        [d for d in input_data if d["metadata"]["Labels"] in ["Click"]]
    ) + len(input_data)

    for out_segment in output_data:  # finding an augmented segment
        if is_augmented(out_segment["metadata"]["segment_uuid"]):
            break
    for in_segment in input_data:  # finding the corresponding input data
        if (
            in_segment["metadata"]["segment_uuid"][:14]
            == out_segment["metadata"]["segment_uuid"][:14]
        ):
            break

    # check if the augmented data is twice as big as the original data
    np.testing.assert_array_equal(2 * in_segment["data"], out_segment["data"])


##########################################################
@pytest.mark.django_db
def test_augmentation_time_stretch(input_data):

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Time Stretch",
        subtype="Supervised",
        input_contract=time_stretch_contracts["input_contract"],
        output_contract=time_stretch_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="time_stretch",
    )

    ##########################################################

    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Time Stretch",
                "inputs": {
                    "stretch_factor_range": [0.95, 1.05],
                    "fraction": 0.1,
                    "target_labels": ["knocking", "Click"],
                    "input_columns": ["channel_0"],
                    "filter": {"Set": "Validate"},
                },
            },
        ],
    )

    assert len(output_data) == len(input_data) + round(
        0.1
        * len(
            [
                d
                for d in input_data
                if d["metadata"]["Labels"] in ["Click", "knocking"]
                and d["metadata"]["Set"] in ["Validate"]
            ]
        )
    )

    ######################################## output :=  input

    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Time Stretch",
                "inputs": {
                    "stretch_factor_range": [1, 1],
                    "fraction": 1,
                    "input_columns": ["channel_0"],
                    "replace": True,
                },
            },
        ],
    )

    # replacing the input data that meets the filter condition with
    # the augmented versions
    assert len(output_data) == len(input_data) + len(input_data)

    for out_segment in output_data:  # finding an augmented segment
        if is_augmented(out_segment["metadata"]["segment_uuid"]):
            break
    for in_segment in input_data:  # finding the corresponding input data
        if (
            in_segment["metadata"]["segment_uuid"][:14]
            == out_segment["metadata"]["segment_uuid"][:14]
        ):
            break

    # check if the augmented data is the same as the original data
    np.testing.assert_array_equal(in_segment["data"], out_segment["data"])


##########################################################


@pytest.mark.django_db
def test_augmentation_pitch_shift(input_data):

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Pitch Shift",
        subtype="Supervised",
        input_contract=pitch_shift_contracts["input_contract"],
        output_contract=pitch_shift_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="pitch_shift",
    )

    ##########################################################

    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Pitch Shift",
                "inputs": {
                    "shift_range": [-4, 4],
                    "step_per_octave": 128,
                    "sample_rate": 16000,
                    "fraction": 0.25,
                    "target_labels": ["knocking"],
                    "input_columns": ["channel_0"],
                    "filter": {"Set": "Test"},
                },
            },
        ],
    )

    assert len(output_data) == len(input_data) + round(
        0.25
        * len(
            [
                d
                for d in input_data
                if d["metadata"]["Labels"] in ["knocking"]
                and d["metadata"]["Set"] in ["Test"]
            ]
        )
    )

    ######################################## output :=  input

    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Pitch Shift",
                "inputs": {
                    "shift_range": [0, 0],
                    "step_per_octave": 4,
                    "sample_rate": 16000,
                    "fraction": 1,
                    "input_columns": ["channel_0"],
                    "replace": True,
                },
            },
        ],
    )

    # replacing the input data that meets the filter condition with
    # the augmented versions
    assert len(output_data) == len(input_data) + len(input_data)

    for out_segment in output_data:  # finding an augmented segment
        if is_augmented(out_segment["metadata"]["segment_uuid"]):
            break
    for in_segment in input_data:  # finding the corresponding input data
        if (
            in_segment["metadata"]["segment_uuid"][:14]
            == out_segment["metadata"]["segment_uuid"][:14]
        ):
            break

    # check if the augmented data is the same as the original data
    # even if pitch shift equals zero, sometimes there are tiny differences which are not significant
    # "atol" is the absolute difference tolerance
    np.testing.assert_allclose(in_segment["data"], out_segment["data"], atol=1)


##########################################################


@pytest.mark.django_db
def test_augmentation_random_crop(input_data):

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Random Crop",
        subtype="Supervised",
        input_contract=random_crop_contracts["input_contract"],
        output_contract=random_crop_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="random_crop",
    )

    ##########################################################
    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Random Crop",
                "inputs": {
                    "crop_size": 9000,
                    "overlap_factor": 0,
                    "target_labels": ["knocking"],
                    "filter": {"Set": "Train"},
                },
            },
        ],
    )

    assert len(output_data) == len(  # filtered and augmented
        [
            d
            for d in input_data
            if d["metadata"]["Labels"] in ["knocking"]
            and d["metadata"]["Set"] in ["Validate"]
        ]
    ) + len(  # not replaced/filtered portion, not augmented
        [
            d
            for d in input_data
            if not d["metadata"]["Labels"] in ["knocking"]
            or not d["metadata"]["Set"] in ["Validate"]
        ]
    )

    for out_segment in output_data:  # finding augmented segments
        if is_augmented(out_segment["metadata"]["segment_uuid"]):
            assert out_segment["data"].shape[1] == 9000
            assert out_segment["statistics"]["length"] == 9000

            for in_segment in input_data:  # finding the corresponding input data
                if (
                    in_segment["metadata"]["segment_uuid"][:14]
                    == out_segment["metadata"]["segment_uuid"][:14]
                ):
                    break

            # Since all queried (filtered) segments lengths is 9000,
            # cropping doesn't change the signal size
            np.testing.assert_array_equal(in_segment["data"], out_segment["data"])

    ##########################################################
    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Random Crop",
                "inputs": {
                    "crop_size": 500,
                    "overlap_factor": -1,
                },
            },
        ],
    )

    # if overlap factor is -1, the default is to return at least
    # one augmented data if possible. when cropping, the original segment is always removed
    assert len(output_data) == 1

    for out_segment in output_data:  # finding augmented segments
        if is_augmented(out_segment["metadata"]["segment_uuid"]):
            assert out_segment["data"].shape[1] == 500
            assert out_segment["statistics"]["length"] == 500

    # the cropped version of an original segment is another original segment
    uid = output_data[0]["metadata"]["segment_uuid"]
    assert is_augmented(uid) == False

    # testing the uuid format of a cropped original segment
    uid_arr = uid.split("-")
    assert uid_arr[2][:3] == "eee"
    assert uid_arr[4][-2:] == "ee"

    output_data = run_augmentation_drive(
        output_data,
        [
            {
                "function_name": "Random Crop",
                "inputs": {
                    "crop_size": 400,
                    "overlap_factor": -1,
                },
            },
        ],
    )

    # the cropped version of an original segment is another original segment
    uid = output_data[0]["metadata"]["segment_uuid"]
    assert is_augmented(uid) == False

    # testing the uuid format of a cropped original segment
    uid_arr = uid.split("-")
    assert uid_arr[2][:3] == "eee"
    assert uid_arr[4][-2:] == "ee"

    # giving an augmented segment to the cropper and
    # it should be replaced by a new segment with uuid format of an augmented segment
    in_data = [copy.deepcopy(input_data[0])]
    in_data[0]["metadata"]["segment_uuid"] = "3a9f297e-b49e-fffa-cdb1-b96e18d05f00"

    out_data = run_augmentation_drive(
        in_data,
        [
            {
                "function_name": "Random Crop",
                "inputs": {
                    "crop_size": 500,
                    "overlap_factor": -1,
                },
            },
        ],
    )

    assert is_augmented(out_data[0]["metadata"]["segment_uuid"]) == True
    assert len(out_data) == 1


##########################################################
in_data_array = np.array(
    [
        [
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -2,
        ],
        [
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            -3,
        ],
        [
            -10,
            -10,
            -10,
            -10,
            -10,
            -10,
            -10,
            -10,
            -10,
            -10,
            -11,
            -11,
            -11,
            -11,
            -11,
            -11,
            -12,
            -12,
            -12,
            -12,
            -12,
            -12,
            -12,
            -12,
            -12,
            -13,
            -13,
            -13,
            -14,
            -14,
            -14,
            -14,
            -15,
            -15,
            -15,
            -15,
            -15,
            -15,
            -16,
            -16,
            -16,
            -16,
            -16,
            -16,
            -15,
            -15,
            -15,
            -15,
            -15,
            -15,
            -14,
            -14,
            -14,
            -14,
            -14,
            -14,
            -14,
            -14,
            -14,
            -15,
        ],
        [
            -16,
            -13,
            -10,
            -8,
            -5,
            -3,
            0,
            2,
            5,
            8,
            12,
            16,
            20,
            23,
            25,
            26,
            28,
            30,
            31,
            33,
            36,
            38,
            40,
            43,
            45,
            48,
            55,
            61,
            67,
            74,
            80,
            87,
            93,
            99,
            105,
            112,
            119,
            127,
            134,
            141,
            149,
            156,
            163,
            169,
            177,
            186,
            194,
            203,
            210,
            218,
            225,
            230,
            235,
            239,
            241,
            243,
            245,
            254,
            263,
            273,
        ],
        [
            -24,
            -23,
            -22,
            -21,
            -18,
            -14,
            -11,
            -10,
            -10,
            -10,
            -9,
            -7,
            -6,
            -5,
            -4,
            -4,
            -4,
            -4,
            -4,
            -5,
            -6,
            -7,
            -8,
            -10,
            -12,
            -14,
            -16,
            -18,
            -21,
            -21,
            -21,
            -21,
            -18,
            -16,
            -14,
            -10,
            -5,
            -1,
            2,
            5,
            7,
            10,
            12,
            14,
            16,
            17,
            18,
            19,
            20,
            22,
            22,
            20,
            19,
            16,
            10,
            5,
            0,
            -4,
            -9,
            -14,
        ],
        [
            46,
            46,
            47,
            48,
            49,
            50,
            51,
            51,
            51,
            51,
            50,
            50,
            50,
            50,
            50,
            50,
            52,
            54,
            56,
            58,
            61,
            63,
            65,
            65,
            65,
            64,
            59,
            55,
            50,
            45,
            41,
            36,
            33,
            30,
            27,
            28,
            29,
            30,
            33,
            36,
            38,
            40,
            41,
            41,
            39,
            36,
            32,
            27,
            22,
            16,
            11,
            6,
            1,
            -3,
            -7,
            -10,
            -14,
            -14,
            -14,
            -15,
        ],
    ],
    dtype=np.int32,
)

##########################################################


@pytest.mark.django_db
def test_augmentation_time_shift():

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Time Shift",
        subtype="Supervised",
        input_contract=pitch_shift_contracts["input_contract"],
        output_contract=pitch_shift_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="time_shift",
    )

    ##########################################################

    in_data = [
        {
            "columns": [
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
            ],
            "metadata": {"CaptureID": 0, "Label": "Unknown", "SegmentID": 13},
            "statistics": {"length": 60},
            "data": in_data_array,
        }
    ]

    # in_data: only one segment which is replaced by the output segment
    out_data = run_augmentation_drive(
        in_data,
        [
            {
                "function_name": "Time Shift",
                "inputs": {
                    "shift_range": [10, 10],
                    "averaging_window_size": 7,
                    "fraction": 1,
                    "replace": True,
                },
            },
        ],
    )

    for data in out_data:
        if data["metadata"]["SegmentID"] != 13:
            break

    np.testing.assert_array_equal(in_data[0]["data"].shape, data["data"].shape)
    np.testing.assert_array_equal(
        np.median(in_data[0]["data"][:, :7], axis=1), data["data"][:, :10][:, 0]
    )


##########################################################


@pytest.mark.django_db
def test_augmentation_resize_segment():

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Resize Segment",
        subtype="Supervised",
        input_contract=pitch_shift_contracts["input_contract"],
        output_contract=pitch_shift_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="resize_segment",
    )

    ##########################################################

    in_data = [
        {
            "columns": [
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
            ],
            "metadata": {"CaptureID": 0, "Label": "Unknown", "SegmentID": 13},
            "statistics": {"length": 60},
            "data": in_data_array,
        }
    ]

    # in_data: only one segment which is replaced by the resized segment
    out_data = run_augmentation_drive(
        in_data,
        [
            {
                "function_name": "Resize Segment",
                "inputs": {
                    "new_size": 23,
                    "averaging_window_size": 7,
                    "fraction": 1,
                    "replace": True,
                },
            },
        ],
    )

    for data in out_data:
        if data["metadata"]["SegmentID"] != 13:
            break

    # new_size
    assert data["data"].shape[1] == 23

    # in_data: only one segment which is replaced by the resized segment
    out_data = run_augmentation_drive(
        in_data,
        [
            {
                "function_name": "Resize Segment",
                "inputs": {
                    "new_size": 103,
                    "padding_value": 3000,
                    "fraction": 1,
                    "replace": True,
                },
            },
        ],
    )

    for data in out_data:
        if data["metadata"]["SegmentID"] != 13:
            break

    data = data["data"]
    assert data.shape[1] == 103  # new_size

    for i in range(data.shape[0]):
        signal = data[i]
        np.testing.assert_array_equal(signal[signal < 3000], in_data[0]["data"][i])


##########################################################


@pytest.mark.django_db
def test_cropping_mixup(input_data):

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Random Crop",
        subtype="Supervised",
        input_contract=random_crop_contracts["input_contract"],
        output_contract=random_crop_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="random_crop",
    )

    Transform.objects.create(
        uuid="fc7aaa9f-7e90-4374-811b-0c37a4de7dd4",
        name="Add Noise",
        subtype="Supervised",
        input_contract=add_noise_contracts["input_contract"],
        output_contract=add_noise_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="add_noise",
    )

    ########################################
    try:
        output_data = run_augmentation_drive(
            input_data,
            [
                {
                    "function_name": "Add Noise",
                    "inputs": {
                        "background_scale_range": [10, 100],
                        "fraction": 0.5,
                        "noise_types": ["white", "pink"],
                        "target_labels": ["knocking"],
                        "filter": {"Set": ["Train", "Validate"]},
                        "input_columns": ["channel_0"],
                    },
                },
                {
                    "function_name": "Random Crop",
                    "inputs": {
                        "crop_size": 9000,
                        "overlap_factor": 0,
                        "target_labels": ["knocking"],
                        "filter": {"Set": "Train"},
                    },
                },
            ],
        )
    except ValidationError:
        assert True


##########################################################
@pytest.mark.django_db
def test_augmentation_time_flip(input_data):

    Transform.objects.create(
        uuid="e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
        name="Time Flip",
        subtype="Supervised",
        input_contract=time_stretch_contracts["input_contract"],
        output_contract=time_stretch_contracts["output_contract"],
        core=True,
        path="core_functions/augmentation.py",
        function_in_file="time_flip",
    )

    ######################################## output :=  flip(input)

    output_data = run_augmentation_drive(
        input_data,
        [
            {
                "function_name": "Time Flip",
                "inputs": {
                    "flipped_label": "unk",
                    "fraction": 1,
                    "input_columns": ["channel_0"],
                    "replace": True,
                },
            },
        ],
    )

    # replacing the input data that meets the filter condition with
    # the augmented versions
    assert len(output_data) == len(input_data) + len(input_data)

    for out_segment in output_data:  # finding an augmented segment
        if is_augmented(out_segment["metadata"]["segment_uuid"]):
            break
    for in_segment in input_data:  # finding the corresponding input data
        if (
            in_segment["metadata"]["segment_uuid"][:14]
            == out_segment["metadata"]["segment_uuid"][:14]
        ):
            break

    # check if the augmented data is the same as the original data
    np.testing.assert_array_equal(in_segment["data"], np.fliplr(out_segment["data"]))

    assert out_segment["metadata"]["Labels"] == "unk"


##########################################################
