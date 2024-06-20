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

from pandas import DataFrame
from library.exceptions import InputParameterException


def tr_feature_average(input_data, group_columns, num_cascades, stride=1):
    """
    Averages cascading features across feature vectors and sets the value of the
    resultant feature vector to their average.

    Args:
        num_cascades: The number of cascaded windows to cover
        stride: After creating first vector, slide a distance over the feature vectors before creating the next
    Returns:
        DataFrame: Returns dataframe of feature vectors
    """

    segs = input_data.groupby([g for g in group_columns if g != "SegmentID"])

    feature_columns = [col for col in input_data.columns if col not in group_columns]

    # return segs
    M = []

    for _, tmp_df in segs:
        indexes = list(tmp_df.sort_values(by="SegmentID").index)
        tmp = tmp_df[group_columns].iloc[0].to_dict()
        # print(tmp_df)

        if len(indexes) < num_cascades:
            continue

        for cascade_start in range(0, len(indexes) - num_cascades + 1, stride):
            tmp.update(
                input_data.iloc[indexes[cascade_start : cascade_start + num_cascades]][
                    feature_columns
                ]
                .mean()
                .to_dict()
            )
            # print(input_data.iloc[indexes[cascade_start]]['SegmentID'])
            assert cascade_start == input_data.iloc[indexes[cascade_start]]["SegmentID"]
            tmp["SegmentID"] = cascade_start

            M.append(copy.deepcopy(tmp))

    return DataFrame(M)


tr_feature_average_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "group_columns", "type": "list"},
        {"name": "num_cascades", "type": "int", "default": 1},
        {"name": "stride", "type": "int", "default": 1},
    ],
    "output_contract": [{"name": "df_out", "type": "DataFrame"}],
}


def range_scale(
    input_data,
    passthrough_columns,
    min_bound=0,
    max_bound=255,
    feature_max=None,
    feature_min=None,
    scale_function="Normal",
):
    """
    Normalize data by scalling them using some function and to a specific integer value range.

    Args:
        min_bound: min value in the output (0~255)
        max_bound: max value in the output (0~255)
        feature_max: Max value to scale by
        feature_min: Minimum value to scale by
        scale: Function to scale by, options: [linear, Log, ln, Exponential, sqrt2, sqrt4]

    Returns:
        Scales all of the data by the same min and max value. This is different
        than Min Max Scale, which scales each feature by different values.

    Examples:
        >>> from pandas import DataFrame
        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],
                            [-2, 8, 7], [2, 9, 6]],
                            columns=['feature1', 'feature2', 'feature3'])
        >>> df['Subject'] = 's01'
        >>> df
            Out:
               feature1  feature2  feature3 Subject
            0        -3         6         5     s01
            1         3         7         8     s01
            2         0         6         3     s01
            3        -2         8         7     s01
            4         2         9         6     s01
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force = True)
        >>> client.pipeline.add_transform('Range Scale',
                params={'passthrough_columns':['Subject'],
                        'feature_min':0, "feature_max":100})
            Out:


    """

    def scale_by_function(tmp_data, scale):
        if scale == "linear":
            return tmp_data
        if scale == "log":
            return np.log(tmp_data)
        if scale == "exp":
            return np.exp(tmp_data)
        if scale == "ln":
            return np.ln(tmp_data)
        if scale == "sqrt2":
            return np.sqrt(tmp_data)
        if scale == "sqrt4":
            return np.power(tmp_data, 0.25)

    cols_to_scale = sorted(
        [col for col in input_data.columns if col not in passthrough_columns]
    )
    df_out = DataFrame()
    input_data[cols_to_scale] = input_data[cols_to_scale].astype(float)

    feature_min_max_parameters = {"minimums": {}, "maximums": {}}

    for col in cols_to_scale:
        new_scale = (
            max_bound
            * (
                (scale_by_function(input_data[col].values, scale) - feature_min)
                / (feature_max - feature_min + 1e-10)
            )
        ).astype(int)

        new_scale = [i if i <= max_bound else max_bound for i in new_scale]
        new_scale = [i if i >= min_bound else min_bound for i in new_scale]
        df_out[col] = new_scale

        feature_min_max_parameters["minimums"][col] = feature_min
        feature_min_max_parameters["maximums"][col] = feature_max

    df_out[passthrough_columns] = input_data[passthrough_columns]

    return df_out, feature_min_max_parameters


range_scale_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "passthrough_columns", "type": "list"},
        {"name": "min_bound", "type": "numeric", "default": 0},
        {"name": "max_bound", "type": "numeric", "default": 255},
        {
            "name": "scale",
            "type": "str",
            "default": "normal",
            "options": [
                {"name": "log"},
                {"name": "ln"},
                {"name": "linear"},
                {"name": "sqrt2"},
                {"name": "sqrt4"},
                {"name": "exp"},
            ],
        },
        {"name": "feature_max", "type": "float"},
        {"name": "feature_min", "type": "float"},
    ],
    "output_contract": [
        {"name": "df_out", "type": "DataFrame"},
        {"name": "feature_min_max_parameters", "type": "list", "persist": True},
    ],
}


def principle_component_analysis(
    input_data, passthrough_columns, n_components=4, feature_pca_components=None
):
    """
    Perform PCA to reduce the dimensionality of the data by projecting the data onto a new set
    to orthogonal vectors starting with vectors that contain the greatest variance to the least.

    Args:
        n_components: Number of components to generate
        feature_pca_components: Dictionary of 'pca eigenvectors'.
            If a non-empty dictionary is passed as parameter, pca eigenvectors will be calculated
        pad: pad the min and max value by +-col.std()/pad. Can be used to make min max more robust to
             unseen data.

    Returns:
        If 'feature_pca_components' values is {} then the minimums
        and maximums for each feature are calculated based on the data passed.
    """

    cols_to_scale = [
        col for col in input_data.columns if col not in passthrough_columns
    ]

    if n_components < 0 or n_components > len(cols_to_scale):
        raise InputParameterException(
            "n_components must be less than total number of features"
        )

    df_out = DataFrame()
    input_data[cols_to_scale] = input_data[cols_to_scale]
    pca = PCA(n_components=n_components)

    pca.fit(input_data[cols_to_scale].values)

    transformed = pca.transform(input_data[cols_to_scale].values)

    component_columns = []
    for i in range(n_components):
        df_out["PCA_COMPONENT_{0:04}".format(i)] = transformed[:, i].astype(int)
        df_out["PCA_COMPONENT_{0:04}".format(i)] = df_out[
            "PCA_COMPONENT_{0:04}".format(i)
        ].apply(lambda x: 0 if x < 0 else x)
        df_out["PCA_COMPONENT_{0:04}".format(i)] = df_out[
            "PCA_COMPONENT_{0:04}".format(i)
        ].apply(lambda x: 255 if x > 255 else x)
        component_columns.append("PCA_COMPONENT_{0:04}".format(i))

    column_dict = {k: v for k, v in enumerate(component_columns + ["Mean"])}
    feature_pca_components = concat(
        [
            DataFrame(np.vstack([pca.components_, pca.mean_]).T),
            DataFrame(np.hstack([pca.explained_variance_.T, 0])).T,
        ]
    )

    feature_pca_components.rename(column_dict)

    df_out[passthrough_columns] = input_data[passthrough_columns]

    return df_out, feature_pca_components.to_dict(orient="record")


principle_component_analysis_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {"name": "passthrough_columns", "type": "list"},
        {"name": "n_components", "type": "numeric", "default": 2},
        {"name": "feature_pca_components", "type": "dict", "default": {}},
    ],
    "output_contract": [
        {"name": "df_out", "type": "DataFrame"},
        {"name": "feature_pca_components", "type": "list", "persist": True},
    ],
}
