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
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import matplotlib.patches as patches
from seaborn import boxplot, violinplot, set_style
from pandas import DataFrame, concat


class Visualize(object):
    def __init__(self, feature_vector=None, model=None, label=None):
        """
        model: model result or knowledgepack
        feature_vector (Dataframe): feature set that is results of generator_set or feature_selector
        label (String), name of class
        """
        self._feature_vector = None
        self._knowledgepack = None
        self._label = None

        self.knowledgepack = model
        self.label = label
        if self.label is None:
            print(
                "Label column is not specified for this knowledgepack, specify as label=XXX"
            )
        self.feature_vector = feature_vector

    @property
    def knowledgepack(self):
        """Auto generated unique identifier for the project object"""
        return self._knowledgepack

    @knowledgepack.setter
    def knowledgepack(self, value):
        if value is None:
            self._knowledgepack = None
        elif hasattr(value, "knowledgepack"):
            self._knowledgepack = value.knowledgepack
        else:
            self._knowledgepack = value

    @property
    def label(self):
        """Auto generated unique identifier for the project object"""
        return self._label

    @label.setter
    def label(self, value):
        if value is None and self.knowledgepack:
            self._label = self.knowledgepack.query_summary.get("label_column", None)
        else:
            self._label = value

    @property
    def feature_vector(self):
        """Auto generated unique identifier for the project object"""
        return self._feature_vector

    @feature_vector.setter
    def feature_vector(self, value):
        self._feature_vector = value[
            [i for i in sorted(value.columns.tolist()) if ("gen_" == i[:4])]
            + [self.label]
        ]

    def plot_features(
        self,
        features_list=None,
        plot_style="boxplot",
        figsize=(20, 5),
        features_per_row=4,
    ):
        """
        Display the distributions of feature values across classes.

        Args:
            features (Dataframe): Feature set that is results of generator_set or feature_selector
            label (String): Name of class label
            features_list (List):  List of features to plot, if None plots all (default: None)
            plot_style (String):  'violinplot' / 'boxplot' to determine style of plot
            figsize (tuple): Size of figure to make
            features_per_row (int): Number of features to show in each row of the plot
        """

        # if features_list is not given use all featues
        if not (features_list):
            features_list = [
                i for i in self.feature_vector.columns.tolist() if ("gen_" == i[:4])
            ]

        # reframe the feature dataframe so it can be used to input for violinplot or boxplot
        num_plots = len(features_list) // (features_per_row)
        if len(features_list) % features_per_row != 0:
            num_plots += 1
        figsize = (figsize[0], figsize[1] * num_plots)
        f, axarr = plt.subplots(num_plots, figsize=figsize)
        set_style("ticks")
        if not isinstance(axarr, np.ndarray):
            axarr = [axarr]

        for index in range(num_plots):
            df_list = [
                reframe(self.feature_vector, feature, self.label)
                for feature in features_list[
                    index * features_per_row : (index + 1) * features_per_row
                ]
            ]

            if plot_style == "violinplot":
                violinplot(
                    x="Features",
                    y="Sensor Values",
                    hue=self.label,
                    data=concat(df_list),
                    palette="muted",
                    ax=axarr[index],
                )
            elif plot_style == "boxplot":
                boxplot(
                    x="Features",
                    y="Sensor Values",
                    hue=self.label,
                    data=concat(df_list),
                    palette="muted",
                    ax=axarr[index],
                )
            else:
                print("Error: plot_style is not in the library")
                return

            axarr[index].set_xticklabels(
                features_list[
                    index * features_per_row : (index + 1) * features_per_row
                ],
                fontsize=12,
                rotation=25,
            )
            axarr[index].set_ylabel("Feature Values", fontsize=16)
            axarr[index].set_xlabel("")
            axarr[index].legend()
            axarr[index].set_ylim((0, 255))
            axarr[index].legend().set_visible(False)

        axarr[-1].set_xlabel("Features", fontsize=16)
        axarr[0].legend(loc="center left", bbox_to_anchor=(1, 0.85), fontsize=16)
        axarr[0].set_title("Feature Vector Distribution", fontsize=16)

        plt.subplots_adjust(hspace=0.9)

        plt.show()

    def neuron_feature_map(
        self,
        feature1,
        features_list,
        label=None,
        norm=None,
        hist_figure=True,
        neuron_figure=True,
        vector_labels=["all"],
        vector_alpha=0.3,
        neuron_alpha=0.2,
        color_list=[
            "m",
            "k",
            "b",
            "lime",
            "r",
            "c",
            "y",
            "brown",
            "tan",
            "g",
            "pink",
            "gray",
        ],
    ):
        """
        This function display neuron map, feature map and feature distributions.

        Args:
            hist_figure = Bool, display historgram of vector for given features.
            neuron_figure = True,
            pivot_feature = String, it is y-axis feature that used to display neuron map, feature map and feature distributions
            versus_features = List<String>, x-axis features that used to display neuron map, feature map and feature distributions
            vector_labels (List): which features will be displayed  [ f1, f2, f3, ..., 'all', [] ], ['all'] display all features, [] does not display any features
            vector_alpha = 0.3, level of vector transparency
            neuron_alpha = 0.1, level of neuron transparency
            norm(int): takes from knowledgepack, to overide 0=L1, 1=LSUP

        Returns: None

        """

        self.hist_figure = hist_figure
        self.pivot_feature = feature1
        self.vector_labels = vector_labels
        self.vector_alpha = vector_alpha
        self.neuron_alpha = neuron_alpha
        self.axis = 10  # axis
        self.color_list = color_list

        if isinstance(features_list, str):
            features_list = [features_list]

        self.columns_index = [None, None]
        self.columns_index[1] = self.feature_vector.columns.tolist().index(
            self.pivot_feature
        )

        for feature in features_list:
            self.columns_index[0] = self.feature_vector.columns.tolist().index(feature)

            if self.vector_labels == ["all"]:
                self.vector_labels = np.unique(self.feature_vector[self.label]).tolist()

            self._set_initial_figure()

            if neuron_figure and self.knowledgepack:
                if norm is None:
                    norm = self.knowledgepack.device_configuration.get(
                        "distance_mode", 0
                    )
                else:
                    norm = norm
                self._plot_neurons(self.knowledgepack.neuron_array, feature, norm)

            if (vector_labels != ["None"]) | (vector_labels == []):
                self._plot_feature_vector(feature)

            self._set_final_figure_settings(feature)
            plt.show()

    def _plot_neurons(self, neurons, versus_feature, norm):
        for neuron in neurons:
            x_val = neuron["Vector"][self.columns_index[0]]
            y_val = neuron["Vector"][self.columns_index[1]]
            aif = neuron["AIF"]

            if neuron["Category"] < 30000:  # if it is not degenerated neuron
                cat_label = self.knowledgepack.class_map[str(neuron["Category"])]
                clr = self.color_list[self.label_indx_list.index(cat_label)]
                if norm == 0:
                    dim = len(neuron["Vector"])
                    new_aif = aif * np.sqrt(2) / dim
                    self.neuron_scatter.add_patch(
                        patches.Rectangle(
                            (x_val - (aif * 2 / dim), y_val),
                            2 * new_aif,
                            2 * new_aif,
                            color=clr,
                            alpha=self.neuron_alpha,
                            angle=-45.0,
                        )
                    )

                else:
                    self.neuron_scatter.add_patch(
                        patches.Rectangle(
                            (x_val - aif, y_val - aif),
                            2 * aif,
                            2 * aif,
                            color=clr,
                            alpha=self.neuron_alpha,
                            angle=0,
                        )
                    )

                self.neuron_scatter.scatter(x_val, y_val, c=clr, marker="*", s=96)

    def _plot_hist(self, Xs, Ys, clr):
        binwidth = 5
        bins = np.arange(0, 256, binwidth)
        self.axHistx.hist(Xs, bins=bins, color=clr, alpha=self.vector_alpha)
        self.axHistx.set_xlim(self.neuron_scatter.get_xlim())

        self.axHisty.hist(
            Ys, bins=bins, color=clr, alpha=self.vector_alpha, orientation="horizontal"
        )
        self.axHisty.set_ylim(self.neuron_scatter.get_ylim())

    def _plot_feature_vector(self, versus_feature):
        for label_indx in self.vector_labels:
            temp_label_data = self.feature_vector[
                self.feature_vector[self.label] == label_indx
            ].index.tolist()
            temp = self.feature_vector.loc[temp_label_data[0]].tolist()
            cat_label = temp[-1]
            clr = self.color_list[self.label_indx_list.index(cat_label)]
            Xs = self.feature_vector.loc[temp_label_data, versus_feature].tolist()
            Ys = self.feature_vector.loc[temp_label_data, self.pivot_feature].tolist()

            self.neuron_scatter.scatter(Xs, Ys, c=clr, alpha=self.vector_alpha)

            if self.hist_figure:
                self._plot_hist(Xs, Ys, clr)

    def _set_initial_figure(self):
        plt.figure(1, figsize=(self.axis, self.axis))

        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.65
        rect_scatter = [left, bottom, width, height]
        self.neuron_scatter = plt.axes(rect_scatter, aspect="equal")

        if self.hist_figure:
            # definitions for the axes
            bottom_h = left_h = left + width + 0.02
            rect_histx = [left, bottom_h, width, 0.2]
            rect_histy = [left_h, bottom, 0.2, height]
            nullfmt = NullFormatter()
            self.axHistx = plt.axes(rect_histx)
            self.axHistx.xaxis.set_major_formatter(nullfmt)
            self.axHisty = plt.axes(rect_histy)
            self.axHisty.yaxis.set_major_formatter(nullfmt)

        if self.knowledgepack:
            self.label_indx_list = np.unique(
                [
                    self.knowledgepack.class_map[str(i)]
                    for i in np.sort(
                        list(map(int, list(self.knowledgepack.class_map.keys())))
                    )
                ]
                + np.unique(self.feature_vector[self.label]).tolist()
            ).tolist()
        else:
            self.label_indx_list = list(np.unique(self.feature_vector[self.label]))

        # this part creates dummy vectors with the unique number of labels for legent.
        for indx in range(len(self.label_indx_list)):
            self.neuron_scatter.scatter(
                0, 0, c=self.color_list[indx], label=self.label_indx_list[indx]
            )

        self.neuron_scatter.set_xlim([0, 256])
        self.neuron_scatter.set_ylim([0, 256])

    def _set_final_figure_settings(self, versus_feature):

        self.neuron_scatter.set_xlabel(versus_feature, fontsize=12)
        self.neuron_scatter.set_ylabel(self.pivot_feature, fontsize=12)

        self.neuron_scatter.set_xticks(range(0, 256, 10))
        self.neuron_scatter.set_xticklabels(range(0, 256, 10), rotation=0, fontsize=8)

        self.neuron_scatter.set_yticks(range(0, 256, 10))
        self.neuron_scatter.set_yticklabels(range(0, 256, 10), rotation=0, fontsize=8)

        if self.hist_figure:
            self.axHistx.set_xticks(range(0, 256, 10))
            self.axHistx.yaxis.set_tick_params(labelsize=8)
            self.axHistx.set_title(self.pivot_feature + " vs " + versus_feature)

            self.axHisty.set_yticks(range(0, 256, 10))
            self.axHisty.xaxis.set_tick_params(labelsize=8)
            self.neuron_scatter.legend(
                loc="center left", bbox_to_anchor=(1.02, 1.26), fontsize=12
            )

        else:
            self.neuron_scatter.legend(
                loc="center left", bbox_to_anchor=(1, 0.945), fontsize=12
            )
            self.neuron_scatter.set_title(self.pivot_feature + " vs " + versus_feature)


def reframe(features, feature, label):
    # This funciton reframes the original features dataframe
    temp_list = DataFrame(columns=[label, "Features", "Sensor Values"])
    temp_list[label] = features[label].tolist()
    temp_list["Features"] = [feature] * len(features)
    temp_list["Sensor Values"] = features[feature].tolist()
    return temp_list
