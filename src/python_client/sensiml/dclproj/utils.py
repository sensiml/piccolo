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

import matplotlib.pyplot as plt
import numpy as np
import scipy
from matplotlib.lines import Line2D
from pandas import DataFrame
from scipy import fftpack, signal
from scipy.sparse import coo_matrix

from sensiml.datamanager.label import LabelSet
from sensiml.datamanager.label_relationship import Segment
from sensiml.datamanager.labelvalue import LabelValueSet
from sensiml.datamanager.segmenter import SegmenterSet


def upload_datasegments(client, datasegments, default_label="Unknown", verbose=True):
    """Upload a segments form DataSegments object

    Args:
        client : logged in Client set to a particular project
        datasegments (DataSegments): DataSegments object containing segments to upload
        default_label (str, optional): Label to use as unknown if DataSegments label is not part of the cloud project. Defaults to "Unknown".
    """

    ls = LabelSet(client._connection, client.project)
    # TODO: Support multiple label groups
    # lvs = {label.name:LabelValueSet(client._connection, client.project, label) for label is ls.labels}
    label = ls.labels[0]
    lvs = LabelValueSet(client._connection, client.project, label).to_dict()
    segmenter_set = SegmenterSet(client._connection, client.project).to_dict()

    if lvs.get(default_label) is None:
        print("Default label is not part of label set")
        return

    default_label_value = lvs[default_label]

    for index, datasegment in enumerate(datasegments):
        capture = client.get_captures()[datasegment.capture]
        label_value = lvs.get(datasegment.label_value, default_label_value)
        segmenter = segmenter_set[datasegment.session]
        tmp_segment = Segment(
            client._connection,
            client.project,
            capture,
            segmenter=segmenter,
            label=label,
            label_value=label_value,
        )
        tmp_segment.uuid = datasegment.uuid
        tmp_segment.sample_start = datasegment.start
        tmp_segment.sample_end = datasegment.end
        if datasegment.uuid:
            tmp_segment.update()
        else:
            tmp_segment.insert()
        if verbose:
            print(capture.filename, index, tmp_segment.uuid)


def confusion_matrix(y_true, y_pred, labels, normalize=None):
    labels = np.asarray(labels)
    n_labels = labels.size
    if n_labels == 0:
        raise ValueError("'labels' should contains at least one label.")
    elif y_true.size == 0:
        return np.zeros((n_labels, n_labels), dtype=int)
    elif len(np.intersect1d(y_true, labels)) == 0:
        raise ValueError("At least one label specified must be in y_true")

    sample_weight = np.ones(y_true.shape[0], dtype=np.int64)

    # check_consistent_length(y_true, y_pred, sample_weight)

    if normalize not in ["true", "pred", "all", None]:
        raise ValueError("normalize must be one of {'true', 'pred', 'all', None}")

    n_labels = labels.size
    # If labels are not consecutive integers starting from zero, then
    # y_true and y_pred must be converted into index form
    need_index_conversion = not (
        labels.dtype.kind in {"i", "u", "b"}
        and np.all(labels == np.arange(n_labels))
        and y_true.min() >= 0
        and y_pred.min() >= 0
    )
    if need_index_conversion:
        label_to_ind = {y: x for x, y in enumerate(labels)}
        y_pred = np.array([label_to_ind.get(x, n_labels + 1) for x in y_pred])
        y_true = np.array([label_to_ind.get(x, n_labels + 1) for x in y_true])

    # intersect y_pred, y_true with labels, eliminate items not in labels
    ind = np.logical_and(y_pred < n_labels, y_true < n_labels)
    if not np.all(ind):
        y_pred = y_pred[ind]
        y_true = y_true[ind]
        # also eliminate weights of eliminated items
        sample_weight = sample_weight[ind]

    # Choose the accumulator dtype to always have high precision
    dtype = np.int64

    cm = coo_matrix(
        (sample_weight, (y_true, y_pred)),
        shape=(n_labels, n_labels),
        dtype=dtype,
    ).toarray()

    with np.errstate(all="ignore"):
        if normalize == "true":
            cm = cm / cm.sum(axis=1, keepdims=True)
        elif normalize == "pred":
            cm = cm / cm.sum(axis=0, keepdims=True)
        elif normalize == "all":
            cm = cm / cm.sum()
        cm = np.nan_to_num(cm)

    return cm


def compute_confusion_matrix(
    predicted, ground_truth, ytick_labels=None, ground_truth_unlabled_is_unknown=False
) -> dict:
    if ytick_labels is None:
        ytick_labels = []

    df_gt = DataFrame(
        [
            "Unlabeled"
            for _ in range(
                max(
                    ground_truth[-1]["capture_sample_sequence_end"],
                    predicted[-1]["capture_sample_sequence_end"],
                )
                + 1
            )
        ],
        columns=["label_value"],
    )

    for segment in ground_truth:
        df_gt.iloc[
            segment["capture_sample_sequence_start"] : segment[
                "capture_sample_sequence_end"
            ]
        ] = segment["label_value"]

    for segment in predicted:
        # print(segment["capture_sample_sequence_start"])
        # print(segment["capture_sample_sequence_end"])
        segment["y_predicted"] = df_gt.iloc[
            segment["capture_sample_sequence_start"] : segment[
                "capture_sample_sequence_end"
            ]
        ]["label_value"].mode()[0]

    combined = DataFrame(predicted)
    if ground_truth_unlabled_is_unknown == False:
        combined = combined[combined["y_predicted"] != "Unlabeled"]

    # TODO: Discuss a better way to handle this situation,  for now I think the best method is to return confusion matrix
    # if not set(combined["Label_Value"].values) <= set(ytick_labels):
    #    return get_empty_confusion_matrix(ytick_labels)

    ytick_labels = list(
        set(combined["label_value"].values.astype(str)).union(ytick_labels)
    )

    ytick_labels = sorted(
        list(set(ytick_labels).union(set(combined["y_predicted"].values.astype(str))))
    )

    cm_array = confusion_matrix(
        y_true=combined["label_value"].astype(str),
        y_pred=combined["y_predicted"].astype(str),
        labels=ytick_labels,
    )

    df_cm = DataFrame(cm_array, index=ytick_labels, columns=ytick_labels).T

    df_cm["Total"] = df_cm.T.sum(axis=0)

    return df_cm


def plot_segments_labels(
    segments,
    data=None,
    labels=None,
    figsize=(30, 4),
    title=None,
    axes=None,
    y_label=(0, 1),
):
    if hasattr(segments, "to_dataframe"):
        segments = segments.to_dataframe()

    if axes is None:
        plt.figure(figsize=figsize)
        currentAxis = plt.gca()
    else:
        currentAxis = axes

    cmap = plt.cm.rainbow

    if labels is None:
        labels = sorted(segments.label_value.unique().tolist())

    if not labels:
        return

    if data is not None:
        y_label = [data.min(), data.max() - data.min()]

    delta = 1 / len(labels)
    label_float = np.arange(0, 1, delta)
    label_float[-1] = 1.0

    label_colors = {labels[index]: cmap(x) for index, x in enumerate(label_float)}
    label_legend = [Line2D([0], [0], color=cmap(x), lw=4) for x in label_float] + [
        Line2D([0], [0], color="white", lw=4)
    ]

    x_lim_end = 0
    for _, seg in segments.iterrows():
        y_origin = y_label[0]
        x_origin = seg["capture_sample_sequence_start"]
        x_final = (
            seg["capture_sample_sequence_end"] - seg["capture_sample_sequence_start"]
        )
        y_final = y_label[1]

        currentAxis.add_artist(
            plt.Rectangle(
                (x_origin, y_origin),
                x_final,
                y_final,
                alpha=0.7,
                color=label_colors[seg["label_value"]],
            )
        )
        x_lim_end = seg["capture_sample_sequence_end"]

    currentAxis.legend(label_legend, labels + [""], loc=1)
    currentAxis.set_xlim(0, x_lim_end)
    currentAxis.set_title(title)

    if data is not None:
        currentAxis.plot(data)


def add_eps(x):
    x[np.where(x == 0)] = scipy.finfo(dtype=x.dtype).eps
    return x


def preemphasis(seq, coeff):
    return np.append(seq[0], seq[1:] - coeff * seq[:-1])


# http://www.practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/
def freq_to_mel(freq):
    return 1125.0 * np.lib.scimath.log(1.0 + freq / 700.0)


def mel_to_freq(mel):
    return 700.0 * (np.exp(mel / 1125.0) - 1.0)


def iter_bin(out, curr_bin, next_bins, backward=False):
    next_bin = next_bins[np.where(next_bins > curr_bin)][0]
    if backward:
        sign = -1
        bias = next_bin
    else:
        sign = 1
        bias = curr_bin
    for f in range(int(curr_bin), int(next_bin)):
        out[f] = sign * (f - bias) / (next_bin - curr_bin)


def mel_filterbank(num_bank, num_freq, sample_freq, low_freq, high_freq):
    num_fft = (num_freq - 1) * 2
    low_mel = freq_to_mel(low_freq)
    high_mel = freq_to_mel(high_freq)
    banks = np.linspace(low_mel, high_mel, num_bank + 2)
    bins = np.floor((num_fft + 1) * mel_to_freq(banks) / sample_freq)
    out = np.zeros((num_bank, num_fft // 2 + 1))
    for b in range(num_bank):
        iter_bin(out[b], bins[b], bins[b + 1 :])
        iter_bin(out[b], bins[b + 1], bins[b + 2 :], backward=True)
    return out


def mfcc(
    data,
    channel,
    sample_freq,
    frame_length=1024,
    frame_shift=0.5,
    remove_dc_offset=True,
    num_ceps=23,
    num_mel_bins=80,
    use_power=True,
    figsize=(30, 4),
    plot_all=True,
):
    """
    data : DataFrame data to use
    channel: channel (column) to use from dataframe
    sampel_rate: the sampel rate of the captured data. The sample rate defines the MFCC
    """

    def add_eps(x):
        x[np.where(x == 0)] = scipy.finfo(dtype=x.dtype).eps
        return x

    def preemphasis(seq, coeff):
        return np.append(seq[0], seq[1:] - coeff * seq[:-1])

    # http://www.practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/
    def freq_to_mel(freq):
        return 1125.0 * np.lib.scimath.log(1.0 + freq / 700.0)

    def mel_to_freq(mel):
        return 700.0 * (np.exp(mel / 1125.0) - 1.0)

    def iter_bin(out, curr_bin, next_bins, backward=False):
        next_bin = next_bins[np.where(next_bins > curr_bin)][0]
        if backward:
            sign = -1
            bias = next_bin
        else:
            sign = 1
            bias = curr_bin
        for f in range(int(curr_bin), int(next_bin)):
            out[f] = sign * (f - bias) / (next_bin - curr_bin)

    def mel_filterbank(num_bank, num_freq, sample_freq, low_freq, high_freq):
        num_fft = (num_freq - 1) * 2
        low_mel = freq_to_mel(low_freq)
        high_mel = freq_to_mel(high_freq)
        banks = np.linspace(low_mel, high_mel, num_bank + 2)
        bins = np.floor((num_fft + 1) * mel_to_freq(banks) / sample_freq)
        out = np.zeros((num_bank, num_fft // 2 + 1))
        for b in range(num_bank):
            iter_bin(out[b], bins[b], bins[b + 1 :])
            iter_bin(out[b], bins[b + 1], bins[b + 2 :], backward=True)
        return out

    window_type = "hamming"

    # Fbank conf
    preemphasis_coeff = 0.97
    high_freq = 0.0  # offset from Nyquist freq [Hz]
    low_freq = 20.0  # offset from 0 [Hz]
    num_lifter = 23

    raw_seq = data[channel].values
    assert raw_seq.ndim == 1  # assume mono
    seq = raw_seq.astype(scipy.float64)
    if remove_dc_offset:
        seq -= np.mean(seq)

    # STFT feat
    seq = preemphasis(seq, preemphasis_coeff)
    window = signal.get_window(window_type, frame_length)
    mode = "psd" if use_power else "magnitude"
    f, t, spectrogram = signal.spectrogram(
        seq,
        sample_freq,
        window=window,
        noverlap=int(frame_length * frame_shift),
        mode=mode,
    )

    # log-fbank feat
    banks = mel_filterbank(
        num_mel_bins,
        spectrogram.shape[0],
        sample_freq,
        low_freq,
        sample_freq // 2 - high_freq,
    )

    fbank_spect = np.dot(banks, spectrogram)
    logfbank_spect = np.log(add_eps(fbank_spect))

    # mfcc feat
    dct_feat = fftpack.dct(logfbank_spect, type=2, axis=0, norm="ortho")[:num_ceps]
    lifter = 1 + num_lifter / 2.0 * np.sin(scipy.pi * np.arange(num_ceps) / num_lifter)

    mfcc_feat = lifter[:, scipy.newaxis] * dct_feat

    if plot_all:
        fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(figsize[0], figsize[1] * 4))
        fig.tight_layout()
        axes[0].plot(seq)
        axes[0].set_title("signal")
        axes[1].imshow(np.log(spectrogram), aspect="auto")
        axes[1].set_title("log(spectrogram)")
        axes[2].matshow(logfbank_spect, aspect="auto")
        axes[2].set_title("logfbank")
        axes[3].matshow(mfcc_feat, aspect="auto")
        axes[3].set_title("mfcc")

        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(figsize[0], figsize[1]))

        for bank in banks:
            axes[0].plot(bank)
            axes[0].set_title("Filter banks")

        axes[1].plot(lifter)
        axes[1].set_title("Litering Coefficients")

        plt.subplots_adjust(hspace=0.2)

    return mfcc_feat
