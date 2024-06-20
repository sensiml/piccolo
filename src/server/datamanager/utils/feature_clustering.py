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
import umap
from django.core.exceptions import ValidationError
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from pandas import DataFrame


class LabelColumnNotFound(Exception):
    pass


class NoFeatureColumnFound(Exception):
    pass


class NotEnoughSamplesException(ValidationError):
    pass


def reduce_dimension_pca(fv, n_components: int = 2):

    z_scaler = StandardScaler()
    Z = z_scaler.fit_transform(fv)

    n_features = fv.shape[1]
    n_size = fv.shape[0]

    max_allowed_components = min(n_size - 1, n_features)
    if n_components > max_allowed_components:
        n_components = max_allowed_components

    pca = PCA(n_components=n_components)
    projections = pca.fit_transform(Z)

    return projections


def resample_data(n_sample, data, label, segment_uuid, index):

    n_data = data.shape[0]
    if n_sample > n_data:
        return data, label, segment_uuid, index

    idx = np.random.choice(range(n_data), n_sample, replace=False)

    return data[idx], label[idx], segment_uuid[idx], index[idx]


class FeatureClustering:
    def __init__(
        self,
        data,
        label_column="Label",
        shuffle_seed: int = 0,
        n_sample: int = 0,
        max_data_size: int = 10000,
    ):
        """
        Parameters:
            data (DataFrame): feature vector dataframe
            label_column (str): name of the column that holds labels
            shuffle_seed (int): random seed to shuffle data
            n_sample (int): maximum number of output rows, (sample is chosen randomly)
            max_data_size (int): maximum number of data sample to process
            max_n_columns (int): maximum number of feature columns to process
            maps (dict): Dictionary that stores the
        """

        if label_column is None:
            raise LabelColumnNotFound

        if n_sample > 1000 or n_sample == 0:
            n_sample = 1000

        np.random.seed(shuffle_seed)

        cols = [col for col in data.columns if col[:4] == "gen_"]
        n_cols = len(cols)

        if n_cols == 0:
            raise NoFeatureColumnFound('Feature column names must start with "gen_" !')

        n_size = data.shape[0]
        idx = np.asarray(range(n_size), dtype=np.int32)
        if n_size > max_data_size:
            idx = np.random.choice(range(n_size), max_data_size, replace=False)

        self.label_column = label_column
        self.label_values = data[self.label_column].values[idx]
        self.n_label = len(list(set(self.label_values)))
        self.fv = data[cols].values[idx]
        self.idx = idx
        self.n_sample = n_sample
        self.segment_uuids = np.empty_like(self.label_values)

        if "segment_uuid" in data:
            self.segment_uuids = data.get("segment_uuid").values[idx]

    def compute_pca(self, n_components: int = 2):

        n_features = self.fv.shape[1]
        nc = max([2, 4 * n_features // 5])
        nc = min(n_features, nc)

        projections = reduce_dimension_pca(self.fv, n_components=nc)

        projections, label, segment_uuid, index = resample_data(
            self.n_sample, projections, self.label_values, self.segment_uuids, self.idx
        )
        n_pca = min(projections.shape[1], n_components)
        PCA_components = {"PCA_" + str(i): projections[:, i] for i in range(n_pca)}

        index = {"random_index": index}
        Label = {self.label_column: label}
        PCA_components = dict(PCA_components, **Label, segment_uuid=segment_uuid)

        return {
            "result": DataFrame.from_dict(PCA_components),
            "n_components": n_pca,
            "n_sample": projections.shape[0],
        }

    def compute_umap(
        self,
        random_state=0,
        n_neighbor: int = 0,
        n_components: int = 2,
        max_analysis_size=1000,
        max_dimension_size=20,
    ):

        if n_neighbor < 2:
            n_neighbor = max(2, self.n_label)

        if self.fv.shape[1] < n_components:
            n_components = self.fv.shape[1]

        ## dimensionality reduction
        data = self.fv
        if data.shape[1] > max_dimension_size and data.shape[0] > max_dimension_size:
            data = reduce_dimension_pca(data, n_components=max_dimension_size)

        ## reducing the number of samples for analysis
        label = self.label_values
        segment_uuid = self.segment_uuids
        index = self.idx
        if data.shape[0] > max_analysis_size:
            data, label, segment_uuid, index = resample_data(
                max_analysis_size, data, label, segment_uuid, index
            )

        if data.shape[0] < 3:
            raise NotEnoughSamplesException(
                "The number of data points in your dataset is too low to create a meaningful UMAP embedding"
            )

        trans = umap.UMAP(
            n_neighbors=n_neighbor, random_state=random_state, n_components=n_components
        )
        projections = trans.fit_transform(data)

        projections, label, segment_uuid, index = resample_data(
            self.n_sample, projections, label, segment_uuid, index
        )

        UMAP_components = {
            "UMAP_" + str(i): projections[:, i] for i in range(projections.shape[1])
        }

        Label = {self.label_column: label}
        index = {"random_index": index}
        UMAP_components = dict(UMAP_components, **Label, segment_uuid=segment_uuid)

        return {
            "result": DataFrame.from_dict(UMAP_components),
            "n_components": n_components,
            "n_neighbor": n_neighbor,
            "n_sample": projections.shape[0],
        }

    def compute_tsne(
        self,
        random_state: int = 0,
        n_components: int = 2,
        method="barnes_hut",
        max_analysis_size=1000,
        max_dimension_size=20,
    ):
        """
        method : str, default='barnes_hut'
        By default the gradient calculation algorithm uses "barnes_hut".
        This approximation runs in O(NlogN) time. Method "exact" runtime is O(N^2) time.
        The exact algorithm should be used when nearest-neighbor errors need to be better than 3%.
        The exact method cannot scale to millions of examples.
        """

        if self.fv.shape[1] < n_components:
            n_components = self.fv.shape[1]

        # barnes_hut condition
        n_components = min(3, n_components)

        ## dimensionality reduction
        data = self.fv
        if data.shape[1] > max_dimension_size:
            data = reduce_dimension_pca(data, n_components=max_dimension_size)

        ## reducing the number of samples for analysis
        label = self.label_values
        segment_uuid = self.segment_uuids
        index = self.idx
        if data.shape[0] > max_analysis_size:
            data, label, segment_uuid, index = resample_data(
                max_analysis_size, data, label, segment_uuid, index
            )

        tsne = TSNE(n_components=n_components, random_state=random_state, method=method)
        projections = tsne.fit_transform(data)

        projections, label, segment_uuid, index = resample_data(
            self.n_sample, projections, label, segment_uuid, index
        )

        TSNE_components = {
            "TSNE_" + str(i): projections[:, i] for i in range(projections.shape[1])
        }

        Label = {self.label_column: label}
        index = {"random_index": index}
        TSNE_components = dict(TSNE_components, **Label, segment_uuid=segment_uuid)

        return {
            "result": DataFrame.from_dict(TSNE_components),
            "n_components": n_components,
            "n_sample": projections.shape[0],
        }
