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

# -----------------------------------------------------------
# time series data augmentation
# -----------------------------------------------------------
import copy
from uuid import UUID, uuid4

import numpy as np
from librosa import effects
from tsaug import Resize


class AugmentationValidationError(Exception):
    pass


codes = {
    "add_noise": "0",
    "scale_amplitude": "1",
    "time_stretch": "2",
    "pitch_shift": "3",
    "random_crop": "4",
    "time_shift": "5",
    "time_flip": "6",
    "resize_segment": "7",
}


common_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataSegment"},
        {
            "name": "target_labels",
            "type": "list",
            "handle_by_set": False,
            "default": [],
            "description": "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        },
        {
            "name": "filter",
            "type": "dict",
            "handle_by_set": False,
            "default": {},
            "no_display": True,
            "description": "A Dictionary to define the desired portion of the input data for augmentation.",
        },
        {
            "name": "selected_segments_size_limit",
            "type": "list",
            "element_type": "int",
            "handle_by_set": False,
            "min_elements": 2,
            "max_elements": 2,
            "description": "Range of the allowed segment lengths for augmentation.",
            "default": [1, 100000],
            "range": [1, 100000000],
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataSegment"}],
}

##########################################################
def noise_psd(N, psd=lambda f: 1):
    X_white = np.fft.rfft(np.random.randn(N))
    S = psd(np.fft.rfftfreq(N))
    # Normalize S
    S = S / np.sqrt(np.mean(S ** 2))
    X_shaped = X_white * S
    return np.fft.irfft(X_shaped)


def PSDGenerator(f):
    return lambda N: noise_psd(N, f)


@PSDGenerator
def white_noise(f):
    return 1


@PSDGenerator
def blue_noise(f):
    return np.sqrt(f)


@PSDGenerator
def violet_noise(f):
    return f


@PSDGenerator
def pink_noise(f):
    return 1 / np.where(f == 0, float("inf"), np.sqrt(f))


noise_functions = {
    "white": white_noise,  # normal Gaussian noise
    "pink": pink_noise,
    "violet": violet_noise,
    "blue": blue_noise,
}
##########################################################

# UUID format:
#     Original Segment: yyyyyyyy-yyyy-xxxx-xxxx-xxxxxxxxxxxx
#     Augmented Segments: yyyyyyyy-yyyy-fffc-xxxx-xxxxxxxnnf01
#     Semi-original Segments: yyyyyyyy-xxxx-eee4-xxxx-xxxxxxxxxxee

#     'y' is the wildcard carried over from the original signal UUIDs.
#     'f' and 'e' are reserved codes for augmented or semi-original (cropped original) segments.
#     'c' is the numeric code of the last augmentation transformation.
#     For the augmented segments, 'nn' is replaced with the checksum control digits.
#     The first 8 digits of UUIDs (yyyyyyyy) are used to find and match the segments of the same origin.


def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


def control_digits_uuid(myuuid):
    x = sum([int("0x" + x, 16) for x in "".join(myuuid.split("-"))[:-5]])
    return hex(x)[-2:]


def is_augmented(myuuid):

    if not is_valid_uuid(myuuid):
        return False

    idd = myuuid.split("-")
    if (
        idd[2][:3] == "fff"
        and idd[4][-3] == "f"
        and idd[4][-5:-3] == control_digits_uuid(myuuid)
    ):
        return True
    return False


def augment_uuid(data_uuid, code="f"):

    if not is_valid_uuid(data_uuid):
        return augment_uuid(str(uuid4()))

    aug_id = copy.deepcopy(data_uuid).split("-")
    xid = str(uuid4()).split("-")[-1][:-5]
    aug_id[3] = aug_id[4][:4]
    aug_id[4] = xid + aug_id[4][-5:]  # placeholder
    aug_id[2] = "fff" + code

    cd_uid = control_digits_uuid("-".join(aug_id))

    if not is_augmented(data_uuid):
        aug_id[4] = xid + cd_uid + "f00"
    else:
        cnt = "f%02d" % (int(aug_id[4][-2:]) + 1)
        aug_id[4] = xid + cd_uid + cnt

    return "-".join(aug_id)


def semi_original_uuid(data_uuid, code="f"):

    if not is_valid_uuid(data_uuid):
        return semi_original_uuid(str(uuid4()))

    aug_id = copy.deepcopy(data_uuid).split("-")
    new_id = str(uuid4()).split("-")
    new_id[2] = "eee" + code
    new_id[4] = new_id[4][:-2] + "ee"
    new_id[0] = aug_id[0]

    return "-".join(new_id)


def similar_root_uuid(augmented_id, original_id):

    if not is_valid_uuid(augmented_id) or not is_valid_uuid(original_id):
        raise Exception("Both arguments must be valid UUID strings!")

    if not augmented_id or not original_id:
        raise Exception("[similar_root_uuid] Invalid arguments!")

    if not is_augmented(augmented_id):
        raise Exception(
            "similar_root_uuid] The first uuid ({}) must follow the augmented format!".format(
                augmented_id
            )
        )

    if is_augmented(original_id):
        raise Exception(
            "similar_root_uuid] The second uuid ({}) should not belong to an augmented segment!".format(
                original_id
            )
        )

    idl1 = augmented_id.split("-")
    idl2 = original_id.split("-")

    if idl1[0] != idl2[0]:
        return False

    if idl1[1] != idl2[1]:
        return False

    return True


def augment_id(data_id):
    return int(
        "%d" % np.random.randint(1, 10)
        + "%02d" % np.random.randint(99)
        + "%06d" % (data_id % 1000000)
    )


def metadata_validator(datasegment, meta_condition=None, length_limit=None):

    metadata = datasegment.get("metadata", None)
    segment_length = datasegment["data"].shape[1]

    if metadata and meta_condition:

        for key in meta_condition:
            if not key in metadata:
                return False

        for key, value in metadata.items():
            if key in meta_condition:
                condition = meta_condition[key]

                if type(condition) == list and not value in condition:
                    return False
                if not type(condition) in [list, dict] and value != condition:
                    return False

    if length_limit:
        mn = min(length_limit)
        mx = max(length_limit)
        if segment_length < mn or segment_length > mx:
            return False

    return True


def get_input_data_index(input_data, **kwargs):

    if len(input_data) == 0:
        return []

    meta_condition = kwargs.get("filter", {})
    label_column = kwargs.get("label_column")
    target_labels = kwargs.get("target_labels")
    length_limit = kwargs.get("selected_segments_size_limit", None)

    if target_labels:
        meta_condition[label_column] = target_labels  # list
    slc = [
        metadata_validator(d, meta_condition=meta_condition, length_limit=length_limit)
        for d in input_data
    ]
    indx = [i for i, x in enumerate(slc) if x]

    return indx


def curate(data, data_range=(-32767, 32767)):

    # int16_max = 32767
    data[data < data_range[0]] = data_range[0]
    data[data > data_range[1]] = data_range[1]
    return data.astype(np.int32)


# the core function for all augmenters except for "Random Crop"
def augmenter_core(
    input_data, segment_transformer, code="f", force_remove_originals=False, **kwargs
):

    fraction = kwargs.get("fraction", 1)

    # augmentable indices
    indx = get_input_data_index(input_data, **kwargs)
    N = len(indx)
    augment_size = max(0, round(fraction * N))

    if augment_size == 0:
        return [], indx, force_remove_originals

    if augment_size <= N:
        replace = False
    else:
        replace = True

    augmented_data = []  # list of datasegments

    for ix in np.random.choice(indx, size=augment_size, replace=replace):

        segment = segment_transformer(copy.deepcopy(input_data[ix]), **kwargs)

        aug_metadata = segment["metadata"]

        if "segment_uuid" in aug_metadata:
            uuid_ = aug_metadata["segment_uuid"]

            # preserving an original segment whose original version is forcefully removed
            # this happens when cropping, or resizing
            if force_remove_originals and not is_augmented(uuid_):
                aug_metadata["segment_uuid"] = semi_original_uuid(
                    uuid_,
                    code=code,
                )
            else:
                aug_metadata["segment_uuid"] = augment_uuid(uuid_, code)

        if "SegmentID" in aug_metadata:
            aug_metadata["SegmentID"] = augment_id(aug_metadata["SegmentID"])

        augmented_data.append(segment)

    return augmented_data, indx, force_remove_originals


def augmenter(code="f", force_remove_originals=False):
    def inner(transformer):
        def wrapper(data, **kwargs):
            return augmenter_core(
                data,
                transformer,
                code=code,
                force_remove_originals=force_remove_originals,
                **kwargs
            )

        wrapper.__name__ = transformer.__name__
        wrapper.__doc__ = transformer.__doc__

        return wrapper

    return inner


def crop(data, size: int):

    n = data.shape[1]

    if n < size:
        raise Exception("Crop size must be less than data size!")

    start_index = np.random.randint(n - size + 1)
    return data[:, start_index : start_index + size], start_index


def update_segment_length(segment, length):
    if not "statistics" in segment:
        segment["statistics"] = {}
    segment["statistics"]["length"] = length
    return segment


##########################################################
@augmenter(code=codes["add_noise"])
def add_noise(segment, **kwargs):
    """
    Add Noise:
        Add random noise to time series.
        The added noise to each sample is independent and follows the distribution provided by the method parameter.

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        noise_types [str]: List of background noise flavors. Accepted values are: "white", "pink", "violet", and "blue".
        input_columns [str]: List of sensors that are transformed by this augmentation.
        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.
        background_scale_range [int, int]: Allowed factor range to scale the background noise. The generated noise is drawn from a normal distribution, with the mean of zero and standard deviation of 1. Then it is scaled according to the provided scaled range to meet the synthetic data characteristics.
        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.

    Returns:
        DataSegment: A list of the datasegments with added background noise.

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)
        >>> client.upload_dataframe("toy_data.csv", df, force=True)
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('toy_data',
                                data_columns=['accelx', 'accely', 'accelz'],
                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],
                                label_column='Class')
        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})

        >>> client.pipeline.add_augmentation(
                                [
                                    {
                                        "name": "Add Noise",
                                        "params": {
                                            "background_scale_range": [100, 200],
                                            "fraction": 1,
                                            "noise_types": ["pink", "white"],
                                            "target_labels": ["Crawling"],
                                            "input_columns": ["accelx", "accely"],
                                    },
                                },

                            ]
                        )

        >>> results, stats = client.pipeline.execute()

        Only "Crawling" segments are augmented by adding noise to their "accelx", and "accely" columns.
        Original segments are NOT removed from the output dataset.

        >>> print(results)
            Out:
                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
                0      332     794    4028  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001
                1      200     753    3988  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001
                2      447     666    3947  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001
                3      480     474    3943  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001
                4      467     839    3988  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001
                5      400     738    4019  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000
                6      676     274    4051  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000
                7      244     503    4049  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000
                8       43     843    4053  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000
                9      441     889    4051  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000
                10     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                11     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                12     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                13     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                14     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                15     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                16     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                17     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                18     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                19     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                20     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                21     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                22     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                23     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                24     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                25     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                26     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                27     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                28     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                29     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1

    """

    scale_range = kwargs.get("background_scale_range")
    noise_types = kwargs.get("noise_types")
    target_sensors = kwargs.get("input_columns")

    size = segment["data"].shape[1]
    scale = np.random.uniform(np.min(scale_range), np.max(scale_range))
    method = np.random.choice(list(set(noise_types))).lower()

    if size % 2 == 1:
        size_even = size + 1
    else:
        size_even = size

    for j, sensor in enumerate(segment["columns"]):
        if sensor in target_sensors:
            segment["data"][j] = curate(
                scale * noise_functions[method](size_even)[:size].reshape(size)
                + segment["data"][j]
            )

    return segment


add_noise_contracts = copy.deepcopy(common_contracts)
add_noise_contracts["input_contract"].extend(
    [
        {
            "name": "noise_types",
            "type": "list",
            "element_type": "str",
            "handle_by_set": False,
            "description": 'List of background noise flavors. Accepted values are: "white", "pink", "violet", and "blue".',
            "default": ["white"],
            "options": [
                {"name": "white"},
                {"name": "pink"},
                {"name": "violet"},
                {"name": "blue"},
            ],
        },
        {
            "name": "input_columns",
            "type": "list",
            "handle_by_set": False,
            "default": [],
            "description": "List of sensors that are transformed by this augmentation.",
        },
        {
            "name": "fraction",
            "type": "float",
            "handle_by_set": False,
            "description": "Fraction of the input data segments that are used for this augmentation.",
            "default": 2,
            "range": [0.1, 5],
        },
        {
            "name": "background_scale_range",
            "type": "list",
            "element_type": "float",
            "handle_by_set": False,
            "min_elements": 2,
            "max_elements": 2,
            "range": [1, 10000],
            "description": "Range of the allowed factor to scale the background noise. The generated noise is drawn from a normal distribution, with the mean of zero and standard deviation of 1. Then it is scaled according to the provided scaled range to meet the synthetic data characteristics.",
            "default": [1, 1000],
        },
        {
            "name": "replace",
            "type": "boolean",
            "handle_by_set": False,
            "description": "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
            "default": False,
        },
    ]
)

##########################################################
@augmenter(code=codes["scale_amplitude"])
def scale_amplitude(segment, **kwargs):
    """
    Scale Amplitude:
        Scaling the target sensor values.
        All targeted sensors of the selected segment are scaled according to a scale factor randomly chosen from the provided scale range.

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        input_columns [str]: List of sensors that are transformed by this augmentation.
        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.
        scale_range [int, int]: Allowed factor range to scale the target signals.
        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.

    Returns:
        DataSegment: A list of the transformed datasegments.

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)
        >>> client.upload_dataframe("toy_data.csv", df, force=True)
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('toy_data',
                                data_columns=['accelx', 'accely', 'accelz'],
                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],
                                label_column='Class')
        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})

        >>> client.pipeline.add_augmentation(
                                        [
                                            {
                                                "name": "Scale Amplitude",
                                                "params": {
                                                    "scale_range": [2, 2],
                                                    "fraction": 1,
                                                    "target_labels": ["Running"],
                                                    "input_columns": ["accelx", "accely"],
                                                },
                                        },
                                        ]
                                    )

        >>> results, stats = client.pipeline.execute()

        Only "Running" segments are augmented by scaling "accelx", and "accely" columns.
        Original segments are NOT removed from the output dataset.

        >>> print(results)
            Out:
                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
                0      -88   -7942     843   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000
                1      -94   -7964     836   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000
                2      -86   -7946     832   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000
                3      -80   -7946     834   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000
                4      -96   -7956     844   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000
                5     -104   -7986     842   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001
                6     -128   -7968     821   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001
                7     -128   -7932     813   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001
                8     -132   -7942     826   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001
                9     -124   -7976     827   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001
                10     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                11     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                12     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                13     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                14     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                15     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                16     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                17     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                18     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                19     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                20     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                21     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                22     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                23     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                24     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                25     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                26     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                27     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                28     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                29     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1

    """

    scale_range = kwargs.get("scale_range")
    target_sensors = kwargs.get("input_columns")

    scale_factor = np.random.uniform(np.min(scale_range), np.max(scale_range))

    for j, sensor in enumerate(segment["columns"]):
        if sensor in target_sensors:
            segment["data"][j] = curate(scale_factor * segment["data"][j])

    return segment


scale_amplitude_contracts = copy.deepcopy(common_contracts)
scale_amplitude_contracts["input_contract"].extend(
    [
        {
            "name": "input_columns",
            "type": "list",
            "handle_by_set": False,
            "default": [],
            "description": "List of sensors that are transformed by this augmentation.",
        },
        {
            "name": "fraction",
            "type": "float",
            "handle_by_set": False,
            "description": "Fraction of the input data segments that are used for this augmentation.",
            "default": 2,
            "range": [0.1, 5],
        },
        {
            "name": "scale_range",
            "type": "list",
            "element_type": "float",
            "handle_by_set": False,
            "min_elements": 2,
            "max_elements": 2,
            "range": [0.01, 10],
            "description": "Range of the allowed factors to scale the target sensors.",
            "default": [0.1, 2],
        },
        {
            "name": "replace",
            "type": "boolean",
            "handle_by_set": False,
            "description": "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
            "default": False,
        },
    ]
)
##########################################################


@augmenter(code=codes["time_stretch"])
def time_stretch(segment, **kwargs):
    """
    Time Stretch:
        Change the temporal resolution of time series. Time stretching/compression is often used to alter the tempo or speed of an audio signal without changing the pitch.
        The resized time series is obtained by linear interpolation of the original time series.

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.
        stretch_factor_range [int, int]: Allowed factor range to resize the target signals. A signal is stretched if factor > 1  and is shrunk if factor < 1 and remains unchanged if factor = 1.
        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.

    Returns:
        DataSegment: A list of the transformed datasegments

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)
        >>> client.upload_dataframe("toy_data.csv", df, force=True)
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('toy_data',
                                data_columns=['accelx', 'accely', 'accelz'],
                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],
                                label_column='Class')
        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})

        >>> client.pipeline.add_augmentation(
                                        [
                                            {
                                                "name": "Time Stretch",
                                                "params": {
                                                    "stretch_factor_range": [0.5, 4],
                                                    "fraction": 1,
                                                    "target_labels": ["Running"],
                                                },
                                        },
                                        ]
                                    )

        >>> results, stats = client.pipeline.execute()

        Only the size of "Running" segments are changed in the augmented segments.
        Original segments are NOT removed from the output dataset.

        >>> print(results)
            Out:
                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
                0      -44   -3971     843   Running    1     s01  e2a80997-346a-fff2-2de7-ffde966f3f00  398000000
                1      -43   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-ffde966f3f00  398000000
                2      -48   -3978     844   Running    1     s01  e2a80997-346a-fff2-2de7-ffde966f3f00  398000000
                3      -44   -3971     843   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                4      -44   -3973     841   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                5      -45   -3976     839   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                6      -46   -3979     837   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                7      -46   -3981     835   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                8      -45   -3979     834   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                9      -44   -3976     833   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                10     -43   -3974     832   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                11     -42   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                12     -41   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                13     -41   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                14     -40   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                15     -41   -3974     836   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                16     -43   -3975     838   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                17     -45   -3976     841   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                18     -48   -3978     844   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000
                19     -52   -3993     842   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                20     -58   -3988     831   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                21     -64   -3984     821   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                22     -64   -3975     817   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                23     -64   -3966     813   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                24     -65   -3968     819   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                25     -66   -3971     826   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                26     -64   -3979     826   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                27     -62   -3988     827   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001
                28     -44   -3971     843   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                29     -45   -3975     840   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                30     -46   -3979     837   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                31     -46   -3981     835   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                32     -45   -3977     834   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                33     -43   -3974     832   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                34     -42   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                35     -41   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                36     -40   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                37     -42   -3974     836   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                38     -45   -3976     840   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                39     -48   -3978     844   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000
                40     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                41     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                42     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                43     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                44     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                45     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                46     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                47     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                48     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                49     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                50     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                51     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                52     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                53     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                54     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                55     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                56     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                57     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                58     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                59     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1

    """

    factor_range = kwargs.get("stretch_factor_range")
    size = segment["data"].shape[1]
    stretch_factor = np.random.uniform(np.min(factor_range), np.max(factor_range))

    new_size = int(stretch_factor * size)

    segment["data"] = curate(Resize(size=new_size).augment(segment["data"]))
    segment = update_segment_length(segment, new_size)

    return segment


time_stretch_contracts = copy.deepcopy(common_contracts)
time_stretch_contracts["input_contract"].extend(
    [
        {
            "name": "fraction",
            "type": "float",
            "handle_by_set": False,
            "description": "Fraction of the input data segments that are used for this augmentation.",
            "default": 2,
            "range": [0.1, 5],
        },
        {
            "name": "stretch_factor_range",
            "type": "list",
            "element_type": "float",
            "handle_by_set": False,
            "min_elements": 2,
            "max_elements": 2,
            "range": [0.9, 1.1],
            "description": "Range of the allowed stretch factors.",
            "default": [0.95, 1.05],
        },
        {
            "name": "replace",
            "type": "boolean",
            "handle_by_set": False,
            "description": "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
            "default": False,
        },
    ]
)
##########################################################


@augmenter(code=codes["pitch_shift"])
def pitch_shift(segment, **kwargs):
    """
    Pitch Shift:
        Pitch shifting is used to change the pitch of an audio signal without changing its tempo or speed.
        Shift the pitch of a waveform by ``n_steps`` steps.

        UUID format:
            Original Segment: yyyyyyyy-yyyy-xxxx-xxxx-xxxxxxxxxxxx
            Augmented Segments: yyyyyyyy-yyyy-fffc-xxxx-xxxxxxxnnf01
            Semi-original Segments: yyyyyyyy-xxxx-eee4-xxxx-xxxxxxxxxxee

            'y' is the wildcard carried over from the original signal UUIDs.
            'f' and 'e' are reserved codes for augmented or semi-original (cropped original) segments.
            'c' is the numeric code of the last augmentation transformation.
            For the augmented segments, 'nn' is replaced with the checksum control digits.
            The first 8 digits of UUIDs (yyyyyyyy) are used to find and match the segments of the same origin.

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        input_columns [str]: List of sensors that are transformed by this augmentation.
        sample_rate (int): Number of recorded samples per second.
        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.
        step_per_octave (int): Number of steps per octave.
        shift_range [float, float]: Range of the allowed number of (fractional) steps to shift.
        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.

    Returns:
        DataSegment: A list of the datasegments with added background noise.


    """

    step_per_octave = kwargs.get("step_per_octave")
    shift_range = kwargs.get("shift_range")
    sample_rate = kwargs.get("sample_rate")
    target_sensors = kwargs.get("input_columns")

    n_steps = np.random.uniform(np.min(shift_range), np.max(shift_range))

    for j, sensor in enumerate(segment["columns"]):
        if sensor in target_sensors:
            segment["data"][j] = curate(
                effects.pitch_shift(
                    segment["data"][j].astype(np.float64),
                    sample_rate,
                    n_steps,
                    bins_per_octave=step_per_octave,
                )
            )

    return segment


pitch_shift_contracts = copy.deepcopy(common_contracts)
pitch_shift_contracts["input_contract"].extend(
    [
        {
            "name": "input_columns",
            "type": "list",
            "handle_by_set": False,
            "default": [],
            "description": "List of sensors that are transformed by this augmentation.",
        },
        {
            "name": "sample_rate",
            "type": "int",
            "handle_by_set": False,
            "default": 16000,
            "description": "Number of recorded samples per second.",
        },
        {
            "name": "fraction",
            "type": "float",
            "handle_by_set": False,
            "description": "Fraction of the input data segments that are used for this augmentation.",
            "default": 2,
            "range": [0.1, 5],
        },
        {
            "name": "step_per_octave",
            "type": "float",
            "range": [8, 256],
            "handle_by_set": False,
            "default": 128,
            "description": "Number of steps per octave.",
        },
        {
            "name": "shift_range",
            "type": "list",
            "element_type": "float",
            "handle_by_set": False,
            "min_elements": 2,
            "max_elements": 2,
            "range": [-64, 64],
            "description": "Range of the allowed number of (fractional) steps to shift",
            "default": [-4, 4],
        },
        {
            "name": "replace",
            "type": "boolean",
            "handle_by_set": False,
            "description": "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
            "default": False,
        },
    ]
)

##########################################################
class DataStats(object):
    def __init__(self, inout_data, indx, crop_size: int):

        self._data = inout_data
        self._crop_size = crop_size
        self._indx = indx
        self._stats, self._n_sample = self._data_sample_count()

    def _data_sample_count(self):

        """
        stats format: [[index, number, cumulative_number, normalized_cumulative], ...]

        where:
            index: the index of the segment
            number: number of samples in the segment
            cumulative_number: cumulative number of samples
            normalized_cumulative: normalized cumulative number of segmented: cumulative_number divided by number of all samples in all segments

        Example stats: [[20, 20000, 0, 0.0],
                        [21, 20000, 20000, 0.0010119958445426631],
                        ...,
                        [3302, 16559, 19746368, 0.9991621180405109]]
        """

        count = 0
        stats = []
        for ix in self._indx:
            segment = self._data[ix]
            size = segment["data"].shape[1]
            if size >= self._crop_size:
                stats.append([ix, segment["data"].shape[1], count, 0])
                count += size

        if len(stats) == 0:
            return None, 0

        n_sample = stats[-1][1] + stats[-1][2]
        for x in stats:
            x[3] = x[2] / n_sample

        return stats, n_sample

    def get_random_index(self):

        if self._stats:
            return [x for x in self._stats if x[3] <= np.random.random()][-1][0]
        else:
            return None

    @property
    def n_sample(self):
        return self._n_sample

    @property
    def stats(self):
        return self._stats

    @property
    def croppable_index_list(self):
        return [x[0] for x in self._stats]


def segment_cropper(segment, **kwargs):

    crop_size = kwargs.get("crop_size")

    segment["data"], start_index = crop(segment["data"], crop_size)
    segment = update_segment_length(segment, crop_size)

    segment["start_index"] = start_index

    return segment


def random_crop(input_data, **kwargs):

    """
    Random Crop:
        Randomly cropping a set of long input segments. A set of output segments of the same size are generated.
        The starting point of each segment is drawn randomly. The odds of larger segments to contribute to the output set are proportional to their size.
        If N samples exist in all input segments, in total, the number of output cropped segments is n = N * (1.0 + overlap_factor) / crop_size, where
        overlap_factor is a real number larger than -1 indicating how tightly the output segments are distribute. Crop_size is the size of the segments in the output set.

        If the UUID of the input segment has the augmented format, the UUID of the output segment would have the augmented format as well.
        If the input segment is an original segment, the UUID of the output segment follows the UUID of a semi-original segment.

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        overlap_factor [float, float]: Allowed overlapping factor range to determined the number of randomly generated cropped signals. The minimum overlap factor is -1 that implied only one cropped output segment. For not having overlapping segments use negative values. Any value larger than 1 causes generating segments that randomly overlap each other.
        crop_size (int): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.

    Returns:
        DataSegment: A list of cropped segments.

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)
        >>> client.upload_dataframe("toy_data.csv", df, force=True)
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('toy_data',
                                data_columns=['accelx', 'accely', 'accelz'],
                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],
                                label_column='Class')
        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})
        >>> client.pipeline.add_augmentation(
                                        [
                                            {
                                                "name": "Random Crop",
                                                "params": {
                                                    "crop_size": 4,
                                                    "overlap_factor": 1,
                                                    "target_labels": ["Crawling"],
                                                },
                                            },
                                        ], overwrite=False,
                                    )
        >>> results, stats = client.pipeline.execute()
        >>> print(results)
            Out:
                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
                0      357     594    4051  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000
                1      333     638    4049  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000
                2      340     678    4053  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000
                3      372     708    4051  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000
                4      410     733    4028  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001
                5      450     733    3988  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001
                6      492     696    3947  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001
                7      518     677    3943  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001
                8      450     733    3988  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001
                9      492     696    3947  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001
                10     518     677    3943  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001
                11     528     695    3988  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001
                12     410     733    4028  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001
                13     450     733    3988  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001
                14     492     696    3947  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001
                15     518     677    3943  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001
                16     357     594    4051  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000
                17     333     638    4049  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000
                18     340     678    4053  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000
                19     372     708    4051  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000
                20     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                21     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                22     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                23     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                24     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                25     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                26     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                27     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                28     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                29     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1

    """

    crop_size = kwargs.get("crop_size")
    overlap_factor = kwargs.get("overlap_factor")

    remove_originals = True

    if overlap_factor < -1:
        raise AugmentationValidationError('"overlap_factor" must be larger than -1.')

    indx = get_input_data_index(input_data, **kwargs)
    if len(indx) == 0 or crop_size < 1:
        return [], indx, remove_originals

    stat_crop = DataStats(input_data, indx, crop_size)
    n_sample = stat_crop.n_sample

    augment_size = int(n_sample * (1.0 + overlap_factor) / crop_size)

    # generating at least one augmentation
    if n_sample > 0 and augment_size == 0:
        augment_size = 1

    if augment_size == 0:
        return [], [], remove_originals

    augmented_data = []  # list of datasegments

    for _ in range(augment_size):

        ix = stat_crop.get_random_index()

        segment = segment_cropper(copy.deepcopy(input_data[ix]), **kwargs)

        aug_metadata = segment["metadata"]

        if "segment_uuid" in aug_metadata:
            uuid_ = aug_metadata["segment_uuid"]

            if is_augmented(uuid_):
                aug_metadata["segment_uuid"] = augment_uuid(
                    uuid_, code=codes["random_crop"]
                )
            else:
                aug_metadata["segment_uuid"] = semi_original_uuid(
                    uuid_, code=codes["random_crop"]
                )
        if "SegmentID" in aug_metadata:
            aug_metadata["SegmentID"] = augment_id(aug_metadata["SegmentID"])

        augmented_data.append(segment)

    return augmented_data, stat_crop.croppable_index_list, remove_originals


##########################################################

random_crop_contracts = copy.deepcopy(common_contracts)
random_crop_contracts["input_contract"].extend(
    [
        {
            "name": "overlap_factor",
            "type": "float",
            "handle_by_set": False,
            "description": "The overlapping degree of the cropped segments. Use any values larger than -1. Use 0 for no overlaps, 1 for 100% overlaps and so on.",
            "default": 0,
            "range": [-1, 1],
        },
        {
            "name": "crop_size",
            "type": "int",
            "handle_by_set": False,
            "default": 100,
            "description": "Lengths of the cropped segments.",
        },
    ]
)

##########################################################


@augmenter(code=codes["time_shift"])
def time_shift(segment, **kwargs):
    """
    Time Shift:
        Shifting segments along the time axis. The segment is padded with the signal average within the window of specified size.

        If the UUID of the input segment has the augmented format, the UUID of the output segment would have the augmented format as well.
        If the input segment is an original segment, the UUID of the output segment follows the UUID of a semi-original segment.

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.
        shift_range [int, int]: The range of allowed shifts along the time axis. Use integer values. Negative (positive) values shift the signal to the left (right).
        averaging_window_size (int): The window size on the opposite side of the shifting direction, within which the signal average is calculated and used for padding the signal.
        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.

    Returns:
        DataSegment: A list of randomly shifted segments.

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)
        >>> client.upload_dataframe("toy_data.csv", df, force=True)
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('toy_data',
                                data_columns=['accelx', 'accely', 'accelz'],
                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],
                                label_column='Class')
        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})
        >>> client.pipeline.add_augmentation(
                                        [
                                {
                                    "name": "Time Shift",
                                    "params": {
                                        "fraction": 1,
                                        "shift_range": [-2,2],
                                        "averaging_window_size": 2,
                                    },
                                },
                            ], overwrite=False,
                        )
        >>> results, stats = client.pipeline.execute()
        >>> print(results)
            Out:
                accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
            0      -64   -3966     813   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001
            1      -66   -3971     826   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001
            2      -62   -3988     827   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001
            3      -64   -3979     826   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001
            4      -64   -3979     826   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001
            5      -43   -3973     832   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000
            6      -40   -3973     834   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000
            7      -48   -3978     844   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000
            8      -44   -3975     839   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000
            9      -44   -3975     839   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000
            10     430     733    4008  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001
            11     410     733    4028  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001
            12     450     733    3988  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001
            13     492     696    3947  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001
            14     518     677    3943  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001
            15     377     569    4019  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000
            16     357     594    4051  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000
            17     333     638    4049  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000
            18     340     678    4053  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000
            19     372     708    4051  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000
            20     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
            21     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
            22     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
            23     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
            24     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
            25     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
            26     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
            27     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
            28     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
            29     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
            30     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
            31     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
            32     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
            33     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
            34     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
            35     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
            36     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
            37     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
            38     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
            39     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1


    """

    shift_range = kwargs.get("shift_range")
    win_size = kwargs.get("averaging_window_size", 0)

    mx = np.max(shift_range)
    mn = np.min(shift_range)
    if mn == mx:
        mx += 1
    shift_size = np.random.randint(mn, mx)

    if shift_size == 0:
        return segment

    signals = segment["data"]

    signal_length = signals.shape[1]
    if win_size > signal_length:
        raise Exception(
            "The averaging window size ({}) is larger than the signal length ({}). \n Segment metadata {}.".format(
                win_size, signal_length, segment["metadata"]
            )
        )

    if (
        shift_size > 0
    ):  # shift right: remove the tail and add a constant value to the head
        m = np.median(signals[:, :win_size], axis=1)
        head = np.vstack(m for i in range(shift_size))
        out_signals = np.concatenate((head, signals[:, :-shift_size].T)).T
        segment["data"] = curate(out_signals)
    else:  # shift left: remove the head, reconstruct the tail
        m = np.median(signals[:, -win_size:], axis=1)
        tail = np.vstack(m for i in range(-shift_size))
        out_signals = np.concatenate((signals[:, -shift_size:].T, tail)).T
        segment["data"] = curate(out_signals)

    return segment


time_shift_contracts = copy.deepcopy(common_contracts)
time_shift_contracts["input_contract"].extend(
    [
        {
            "name": "fraction",
            "type": "float",
            "handle_by_set": False,
            "description": "Fraction of the input data segments that are used for this augmentation.",
            "default": 2,
            "range": [0.1, 5],
        },
        {
            "name": "shift_range",
            "type": "list",
            "element_type": "int",
            "handle_by_set": False,
            "min_elements": 2,
            "max_elements": 2,
            "description": "The range of allowed shifts along the time axis. Use integer values. Negative (positive) values shift the signal to the left (right).",
            "default": [-100, 100],
        },
        {
            "name": "averaging_window_size",
            "type": "int",
            "handle_by_set": False,
            "description": "The window size on the opposite side of the shifting direction, within which the signal average is calculated and used for padding the signal.",
            "default": 10,
        },
        {
            "name": "replace",
            "type": "boolean",
            "handle_by_set": False,
            "description": "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
            "default": False,
        },
    ]
)


##########################################################
@augmenter(code=codes["resize_segment"], force_remove_originals=True)
def resize_segment(segment, **kwargs):

    """
    Resize Segment:
        Resizing segments. Segment is padded with the average within a window or with the input padding value.

        If the UUID of the input segment has the augmented format, the UUID of the output segment would have the augmented format as well.
        If the input segment is an original segment, the UUID of the output segment follows the UUID of a semi-original segment.

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        new_size (int): The output segment size.
        averaging_window_size (int): The window size on the opposite side segment, within which the signal average is calculated and used for padding. 'padding_value' is used if the provided window size is not positive.
        padding_value (int): The value used to pad signals when resizing. This parameter is only effective when the input 'averaging_window_size' is not positive.
        replace (boolean): Replacing segment with the resized versions.

    Returns:
        DataSegment: A list of randomly shifted segments.

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)
        >>> client.upload_dataframe("toy_data.csv", df, force=True)
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('toy_data',
                                data_columns=['accelx', 'accely', 'accelz'],
                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],
                                label_column='Class')
        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})
        >>> client.pipeline.add_augmentation(
                                        [
                                            {
                                                "name": "Resize Segment",
                                                "params": {
                                                    "new_size": 10,
                                                    "padding_value": 9999,
                                                },
                                            },
                                        ], overwrite=False,
                                    )
        >>> results, stats = client.pipeline.execute()
        >>> print(results)
        >>> # padded with 9999 on both end, original segments are replaced by the resize semi-original segments
            Out:
                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
                0     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                1      -52   -3993     842   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                2      -64   -3984     821   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                3      -64   -3966     813   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                4      -66   -3971     826   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                5      -62   -3988     827   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                6     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                7     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                8     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                9     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001
                10    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                11     377     569    4019  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                12     357     594    4051  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                13     333     638    4049  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                14     340     678    4053  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                15     372     708    4051  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                16    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                17    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                18    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                19    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000
                20    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                21     410     733    4028  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                22     450     733    3988  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                23     492     696    3947  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                24     518     677    3943  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                25     528     695    3988  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                26    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                27    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                28    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                29    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001
                30     -44   -3971     843   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                31     -47   -3982     836   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                32     -43   -3973     832   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                33     -40   -3973     834   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                34     -48   -3978     844   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                35    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                36    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                37    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                38    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000
                39    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000

    """

    new_size = kwargs.get("new_size")
    win_size = kwargs.get("averaging_window_size", 0)

    signals = segment["data"]
    signal_length = signals.shape[1]

    if new_size <= 0 or new_size == signal_length:
        return segment

    if win_size > signal_length:
        raise Exception(
            "The averaging window size ({}) must be smaller than the signal length ({}). \n Segment metadata {}.".format(
                win_size, signal_length, segment["metadata"]
            )
        )

    size_difference = np.abs(signal_length - new_size)
    head_size = np.random.randint(0, size_difference)
    tail_size = size_difference - head_size

    if new_size < signal_length:
        segment["data"] = curate(signals[:, head_size:-tail_size])
        return segment

    if win_size > 0:
        head_value = np.median(signals[:, :win_size], axis=1)
        tail_value = np.median(signals[:, -win_size:], axis=1)
    else:
        head_value = tail_value = np.full(
            signals.shape[0], kwargs.get("padding_value", 0)
        )

    out_signals = signals.T
    if head_size > 0:
        head = np.vstack(head_value for i in range(head_size))
        out_signals = np.concatenate((head, out_signals))
    if tail_size > 0:
        tail = np.vstack(tail_value for i in range(tail_size))
        out_signals = np.concatenate((out_signals, tail))

    segment["data"] = curate(out_signals.T)

    return segment


resize_segment_contracts = copy.deepcopy(common_contracts)
resize_segment_contracts["input_contract"].extend(
    [
        {
            "name": "new_size",
            "type": "int",
            "handle_by_set": False,
            "description": "Desired size of the segment.",
            "default": 10,
        },
        {
            "name": "padding_value",
            "type": "int",
            "handle_by_set": False,
            "description": "The value used to pad signals when resizing. This parameter is only effective when the input 'averaging_window_size' is not positive.",
            "default": 0,
        },
        {
            "name": "averaging_window_size",
            "type": "int",
            "handle_by_set": False,
            "description": "The window size on the opposite side segment, within which the signal average is calculated and used for padding. 'padding_value' is used if the provided window size is not positive.",
            "default": 0,
        },
        {
            "name": "replace",
            "type": "boolean",
            "handle_by_set": False,
            "description": "Replacing segment with the resized versions.",
            "default": True,
        },
    ]
)

##########################################################


@augmenter(code=codes["time_flip"])
def time_flip(segment, **kwargs):
    """
    Time Flip:
        Flip the signal along the time axis.
        This augmentation is used to decrease the false positive rate by increasing the model sensitivity to feed-forward signals.
        The label of the flipped signal is different than the label of the original signal, usually "Unknown".

    Args:
        input_data [DataSegment]: Input data
        target_labels [str]: List of labels that are affected by this augmentation.
        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.
        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.
        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.
        flipped_label (str): Label of the flipped segment. Most often this label si different than the original label of the segment such as "Unknown" and "Noise".
        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.

    Returns:
        DataSegment: A list of the transformed datasegments

    Example:
        >>> client.pipeline.reset()
        >>> df = client.datasets.load_activity_raw_toy()
        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)
        >>> client.upload_dataframe("toy_data.csv", df, force=True)
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('toy_data',
                                data_columns=['accelx', 'accely', 'accelz'],
                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],
                                label_column='Class')
        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})

        >>> client.pipeline.add_augmentation(
                                        [
                                            {
                                                "name": "Time Flip",
                                                "params": {
                                                    "fraction": 1,
                                                    "flipped_label": "Unknown",
                                                },
                                        },
                                        ]
                                    )

        >>> results, stats = client.pipeline.execute()

        >>> print(results)
            Out:
                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
                0      372     708    4051   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000
                1      340     678    4053   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000
                2      333     638    4049   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000
                3      357     594    4051   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000
                4      377     569    4019   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000
                5      -62   -3988     827   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001
                6      -66   -3971     826   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001
                7      -64   -3966     813   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001
                8      -64   -3984     821   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001
                9      -52   -3993     842   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001
                10     528     695    3988   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001
                11     518     677    3943   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001
                12     492     696    3947   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001
                13     450     733    3988   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001
                14     410     733    4028   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001
                15     -48   -3978     844   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000
                16     -40   -3973     834   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000
                17     -43   -3973     832   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000
                18     -47   -3982     836   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000
                19     -44   -3971     843   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000
                20     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                21     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                22     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                23     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                24     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
                25     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                26     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                27     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                28     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                29     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
                30     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                31     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                32     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                33     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                34     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
                35     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                36     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                37     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                38     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
                39     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1


    """

    flipped_label = kwargs.get("flipped_label", "Unknown")
    label_column = kwargs.get("label_column")

    segment["data"] = np.fliplr(segment["data"])
    segment["metadata"][label_column] = flipped_label

    return segment


time_flip_contracts = copy.deepcopy(common_contracts)
time_flip_contracts["input_contract"].extend(
    [
        {
            "name": "fraction",
            "type": "float",
            "handle_by_set": False,
            "description": "Fraction of the input data segments that are used for this augmentation.",
            "default": 0.5,
            "range": [0.1, 1],
        },
        {
            "name": "flipped_label",
            "type": "str",
            "handle_by_set": False,
            "description": "Label of the flipped segment.",
            "default": "Unknown",
        },
        {
            "name": "replace",
            "type": "boolean",
            "handle_by_set": False,
            "description": "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
            "default": False,
        },
    ]
)
