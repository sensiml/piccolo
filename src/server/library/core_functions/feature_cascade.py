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

import copy
from typing import List, Optional

import numpy as np
import pandas as pd
from pandas import DataFrame, concat


class FeatureCascadeException(Exception):
    pass


def get_dataframe_dtype(df):
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            return np.float32

    return np.int32


def feature_cascade(
    input_data: DataFrame,
    feature_table: DataFrame,
    group_columns: List[str],
    num_cascades: int = 1,
    slide: bool = False,
    training_slide: bool = False,
    training_delta: Optional[int] = None,
) -> DataFrame:
    """
    Flattens feature vectors over a specified number of segments.

    Args:
        input_data (DataFrame): The input dataset.
        feature_table (DataFrame): The feature table to be used for flattening the input data.
        group_columns (List[str]): The list of columns used for grouping data.
        num_cascades (int): The number of cascaded windows to cover.
        slide (bool): If True, after creating first vector, slide and create another vector until all possible cascades
                      for this segment are created. This parameter is only used when creating a Knowledge Pack.
        training_slide (bool): If True, similar to slide, but it is used during the training process for data augmentation
                               purposes when available data size is rather small.
        training_delta (Optional[int]): If provided, it specifies the offset between the beginning of each cascade during
                                        training mode.

    Returns:
        DataFrame: A DataFrame of feature vectors.
    """

    if training_slide and training_delta and training_delta > num_cascades:
        training_delta = num_cascades

    if "CascadeID" in input_data.columns:
        columns_grouped_on = [g for g in group_columns if g != "CascadeID"]

    else:
        columns_grouped_on = [g for g in group_columns if g != "SegmentID"]

    segs = input_data.groupby(columns_grouped_on)
    feature_columns = [col for col in input_data.columns if col not in group_columns]

    cascade_feature_columns = []

    for c in range(num_cascades):
        for i in range(len(feature_columns)):
            cascade_feature_columns.append(
                "gen_c{}_".format(str(c).zfill(4)) + feature_columns[i]
            )

    M = []

    counter = 0

    if training_slide:
        if training_delta is None:
            training_delta = num_cascades
        seg_sizes = (
            segs.size().values - (num_cascades - training_delta)
        ) // training_delta
        seg_sizes[seg_sizes < 0] = 0
        num_rows = seg_sizes.sum()
    else:
        num_rows = segs.ngroups

    num_features = len(feature_columns)

    features_values = np.empty(
        (num_rows, num_features * num_cascades),
        dtype=get_dataframe_dtype(input_data[feature_columns]),
    )

    counter = 0

    for key, tmp_df in segs:

        if not isinstance(key, tuple):
            key = (key,)

        if tmp_df.shape[0] < num_cascades:
            continue

        index_finish = tmp_df.shape[0] - num_cascades + 1
        cascaded_segment = tmp_df[feature_columns].values.flatten()

        tmp = {x[0]: x[1] for x in zip(columns_grouped_on, key)}
        if training_slide:
            M.extend(
                [
                    {**tmp, "CascadeID": index, "SegmentID": x[0], "SegmentIDEnd": x[1]}
                    for index, x in enumerate(
                        zip(
                            tmp_df.SegmentID.values[:index_finish:training_delta],
                            tmp_df.SegmentID.values[num_cascades - 1 :: training_delta],
                        )
                    )
                ]
            )
        else:
            M.extend(
                [
                    {
                        **tmp,
                        "CascadeID": 0,
                        "SegmentID": tmp_df.SegmentID.values[0],
                        "SegmentIDEnd": tmp_df.SegmentID.values[num_cascades - 1],
                    }
                ]
            )

        if training_slide is False:
            features_values[counter] = cascaded_segment[0 : num_cascades * num_features]
            counter += 1

        else:
            for cascade_start in range(0, index_finish, training_delta):
                features_values[counter] = cascaded_segment[
                    cascade_start
                    * num_features : (cascade_start + num_cascades)
                    * num_features
                ]
                counter += 1

    if not M:
        raise FeatureCascadeException(
            "No features were generated. The slide for feature cascade is probably too large."
        )

    df = DataFrame(features_values, columns=cascade_feature_columns)
    df = df.join(DataFrame(M))
    df = (
        df[df.SegmentIDEnd - df.SegmentID == num_cascades - 1]
        .drop("SegmentIDEnd", axis=1)
        .reset_index(drop=True)
    )

    Feature_M = []

    if (feature_table is not None) and (len(feature_table) > 0):
        for i in range(num_cascades):
            tmp_df = copy.deepcopy(feature_table)
            tmp_df["CascadeIndex"] = i
            tmp_df["Feature"] = tmp_df["Feature"].apply(
                lambda x: "gen_c{}_".format(str(i).zfill(4)) + x
            )
            Feature_M.append(copy.deepcopy(tmp_df))
        feature_table = concat(Feature_M).reset_index(drop=True)
    else:
        feature_table = DataFrame(
            {
                "Feature Generator": cascade_feature_columns,
                "CascadeIndex": [int(x[5:9]) for x in cascade_feature_columns],
            }
        )

    return df, feature_table


feature_cascade_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list"},
        {
            "name": "num_cascades",
            "type": "int",
            "default": 1,
            "range": [1, 100],
            "description": "The number of consecutive segments of data that will be combined to produce a final feature vector",
        },
        {
            "name": "slide",
            "type": "boolean",
            "default": True,
            "description": "When slide is True, classifications will be continuously created with each new feature cascade. The Slide setting will be used when generating the Knowledge Pack. When Slide is False, all features banks will be discarded after any classification made by the Knowledge Pack.",
        },
        {
            "name": "training_slide",
            "type": "boolean",
            "default": True,
            "description": "When Training Slide is True, feature vectors will be successively generated with each new feature cascade. Training Slide is often used for data augmentation during the training process, specially when the data size is small.",
        },
        {
            "name": "training_delta",
            "type": "int",
            "range": [1, 100],
            "default": None,
            "description": "When Training Slide is True, the delta value is how much to slide after creating a segment.",
            "depends_on": [{"name": "train_slide", "how": "less_than"}],
        },
    ],
    "output_contract": [
        {"name": "df_out", "type": "DataFrame", "metadata_columns": ["CascadeID"]}
    ],
}
