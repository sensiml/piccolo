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

from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D


def plot_segments(
    segments,
    capture=None,
    capture_name=None,
    labels=None,
    current_start=0,
    ylim=None,
    figsize: Tuple = (30, 8),
    currentAxis=None,
    xlim=None,
):

    if currentAxis is None:
        if capture is not None:
            currentAxis = capture.plot(figsize=figsize)
        else:
            plt.figure(figsize=figsize)
            currentAxis = plt.gca()

    cmap = plt.cm.rainbow

    if capture is not None:
        y_min = capture.describe().loc["min"].min()
        y_max = capture.describe().loc["max"].max()
        x_min = 0
        x_max = capture.shape[0]
    else:
        y_min = 0
        y_max = 1
        x_min = 0
        x_max = segments[-1].end

    if ylim:
        y_min = ylim[0]
        y_max = ylim[1]

    if labels is None:
        labels = segments.label_values

    delta = 1 / len(labels)
    label_float = np.arange(0, 1, delta)
    label_float[-1] = 1.0

    label_colors = {labels[index]: cmap(x) for index, x in enumerate(label_float)}
    label_legend = [Line2D([0], [0], color=cmap(x), lw=4) for x in label_float] + [
        Line2D([0], [0], color="white", lw=4)
    ]

    for index, seg in segments.iterrows():
        y_origin = y_min

        x_origin = seg["capture_sample_sequence_start"] + current_start
        x_final = (
            seg["capture_sample_sequence_end"] - seg["capture_sample_sequence_start"]
        )
        y_final = y_max - y_min

        currentAxis.add_artist(
            plt.Rectangle(
                (x_origin, y_origin),
                x_final,
                y_final,
                alpha=0.2,
                color=label_colors[seg["label_value"]],
            )
        )

    if xlim:
        currentAxis.set_xlim(left=xlim[0], right=xlim[1])
    else:
        currentAxis.set_xlim(left=x_min, right=x_max)

    currentAxis.legend(label_legend, labels + [""], loc=4, ncol=len(label_legend))
    """
    if capture_name:
        currentAxis.text(
            current_start,
            y_max,
            capture_name,
            style="italic",
        )
    """


def plot_threshold_space(
    capture,
    column,
    datasegments=None,
    labels=None,
    threshold_type="sum",
    threshold_width=25,
    xlim=None,
    figsize=(16, 4),
):
    M = []
    for i in range(capture.shape[0]):
        if threshold_type == "absolute sum":
            M.append(np.abs(capture[column].values[i : i + threshold_width]).sum())
        elif threshold_type == "sum":
            M.append(capture[column].values[i : i + threshold_width].sum())
        elif threshold_type == "std":
            M.append(capture[column].values[i : i + threshold_width].std())
        elif threshold_type == "variance":
            M.append(capture[column].values[i : i + threshold_width].var())
        else:
            print("Invalid threshold type")
            return

    test_capture = pd.DataFrame(M)
    if xlim is None:
        xlim = (0, len(M))
    ax = test_capture.plot(figsize=figsize, xlim=xlim)
    if datasegments is not None:
        datasegments.plot_segments(
            figsize=figsize,
            capture=test_capture,
            currentAxis=ax,
            labels=labels,
            xlim=xlim,
        )
