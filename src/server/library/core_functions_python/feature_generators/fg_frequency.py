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
import librosa
import math
from numpy import (
    argmax,
    array,
    concatenate,
    diff,  # for physical features
    divide,
    fft,
    float64,
    hstack,
    int64,
    linalg,
    linspace,
    log2,
    mean,
    median,
    multiply,
    nan,
    ndarray,
    percentile,
    real,
    square,
    std,
    subtract,
)
from pandas import DataFrame

np.seterr(divide="ignore", invalid="ignore")


def calc_dominant_frequency(data, fs):
    freq = fft.fftfreq(len(data), divide(1.0, fs))
    PSD = abs(fft.fft(data))
    dominantFrequency = freq[PSD[1 : len(data) / 2].argmax() + 1]
    return dominantFrequency


def calc_spectral_entropy(data):
    """Test comment through browser"""
    SAMPLELENOFPIBY2 = 512
    ft = fft.fft(data, SAMPLELENOFPIBY2)
    PSD = (ft * ft.conjugate()).real
    P = divide(PSD, sum(PSD + 1e-12))
    logP = log2(P + 1e-12)
    entropy = -sum(multiply(P, logP))
    return entropy


def peak_frequencies(
    input_data,
    columns,
    sample_rate,
    window_type,
    num_peaks,
    min_frequency,
    max_frequency,
    threshold,
    **kwargs
):
    """
    Calculate the peak frequencies for each specified signal. For each column,
    find the frequencies at which the signal has highest power.

    Args:
        columns: List of columns on which `dominant_frequency` needs to be calculated

    Returns:
        DataFrame of `peak frequencies` for each column and the specified group_columns

    """

    if len(input_data) > settings.MAX_FFT_SIZE:
        raise Exception(
            "Max segment length allowed allowed for this feature generator is {}".format(
                settings.MAX_FFT_SIZE
            )
        )

    if window_type.lower() not in ["hanning", "boxcar"]:
        raise Exception("window type must be either hanning or boxcar")

    def find_peaks(x, width, width2, freq, min_cutoff=None, max_cutoff=None):
        peaks = []
        for index in range(width2, len(x) - width2):

            if min_cutoff and freq[index] < min_cutoff:
                continue

            if max_cutoff and freq[index] > max_cutoff:
                return peaks

            if abs(x[index]) > abs(x[index - width : index]).mean():
                if abs(x[index]) > abs(x[index + 1 : index + width + 1]).mean():
                    if abs(x[index]) > abs(x[index - width2 : index]).mean():
                        if (
                            abs(x[index])
                            > abs(x[index + 1 : index + width2 + 1]).mean()
                        ):
                            peaks.append([abs(x[index]), freq[index]])
        return peaks

    freq_data = {}
    for column in columns:
        s = input_data[column].values - input_data[column].mean()
        w = np.fft.rfft(s * get_window(window_type, len(input_data)), n=512)
        freqs = np.fft.rfftfreq(512, d=1.0 / sample_rate)
        peaks = find_peaks(
            abs(w) / abs(w).max(), 1, 2, freqs, min_frequency, max_frequency
        )
        s_peaks = sorted(peaks, reverse=True)
        peaks_freq = sorted(
            [[x[1], x[0]] for index, x in enumerate(s_peaks) if index < num_peaks]
        )

        for i in range(num_peaks):
            if len(peaks_freq) > i and peaks_freq[i][1] > threshold:
                freq_data[column + "PeakFreq{}".format(i + 1)] = peaks_freq[i][0]
            else:
                freq_data[column + "PeakFreq{}".format(i + 1)] = 0

    return DataFrame([freq_data])


peak_frequencies_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "sample_rate",
            "type": "numeric",
            "handle_by_set": True,
            "description": "Sample rate of the sensor data",
            "default": 100,
        },
        {
            "name": "window_type",
            "type": "str",
            "handle_by_set": True,
            "description": "window function to use before fft",
            "default": "hanning",
        },
        {
            "name": "num_peaks",
            "type": "numeric",
            "handle_by_set": True,
            "default": 2,
            "description": "number of frequency peaks to find",
        },
        {
            "name": "min_frequency",
            "type": "numeric",
            "handle_by_set": True,
            "description": "min cutoff frequency",
            "default": 0,
        },
        {
            "name": "max_frequency",
            "type": "numeric",
            "handle_by_set": True,
            "description": "max cutoff frequency",
            "default": 1000,
        },
        {
            "name": "threshold",
            "type": "numeric",
            "handle_by_set": True,
            "description": "threshold value a peak must be above",
            "default": 0.2,
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def chroma_core(
    chroma,
    vector,
    sample_rate,
    n_fft,
    window_size,
    cepstra_count,
    computation_source,
    params=None,
):

    if computation_source == "waveform":
        # Compute from a waveform
        if chroma == "chromagram":
            return librosa.feature.chroma_stft(
                y=vector,
                sr=sample_rate,
                norm=None,
                n_fft=n_fft,
                hop_length=window_size,
                n_chroma=cepstra_count,
            )
        elif chroma == "constantQ":
            return librosa.feature.chroma_cqt(
                y=vector, sr=sample_rate, n_chroma=cepstra_count, norm=False
            )
        elif chroma == "CENS":
            return librosa.feature.chroma_cens(
                y=vector, sr=sample_rate, n_chroma=cepstra_count, norm=False
            )
        elif chroma == "RMSE":
            # !!! cepstra_count is used as a delta paramenter !!!
            return librosa.feature.rmse(
                y=vector, frame_length=window_size, hop_length=cepstra_count
            )
        elif chroma == "spectral_cent":
            return librosa.feature.spectral_centroid(
                y=vector, sr=sample_rate, n_fft=n_fft, hop_length=window_size
            )
        elif chroma == "spectral_band":
            # !!! sample rate is used to carry p value
            return librosa.feature.spectral_bandwidth(
                y=vector, p=sample_rate, n_fft=n_fft, hop_length=window_size, norm=False
            )
        elif chroma == "spectral_cont":
            return librosa.feature.spectral_contrast(
                y=vector,
                sr=sample_rate,
                n_fft=n_fft,
                hop_length=window_size,
                n_bands=params["number_of_bands"],
                fmin=params["frq_min"],
            )
        elif chroma == "spectral_flat":
            return librosa.feature.spectral_flatness(
                y=vector, n_fft=n_fft, hop_length=window_size
            )
        elif chroma == "spectral_roll":
            return librosa.feature.spectral_rolloff(
                y=vector,
                sr=sample_rate,
                roll_percent=params,
                n_fft=n_fft,
                hop_length=window_size,
            )
        elif chroma == "polynomial":
            return librosa.feature.poly_features(
                y=vector, order=params, n_fft=n_fft, hop_length=window_size
            )
        elif chroma == "tonnetz":
            vector_hr = librosa.effects.harmonic(vector, margin=params)
            return librosa.feature.tonnetz(y=vector_hr, sr=sample_rate, chroma=None)
        elif chroma == "ZCRA":
            return librosa.feature.zero_crossing_rate(
                vector, frame_length=window_size, hop_length=params
            )
        elif chroma == "MFCCLib":
            return librosa.feature.mfcc(y=vector, sr=sample_rate, n_mfcc=cepstra_count)
        elif chroma == "oenv":
            return [
                librosa.onset.onset_strength(
                    y=vector, sr=sample_rate, hop_length=window_size
                )
            ]
        elif chroma == "tempogram":
            # variables are arranged intentially
            oenv = librosa.onset.onset_strength(
                y=vector, sr=sample_rate, hop_length=window_size
            )
            return librosa.feature.tempogram(
                onset_envelope=oenv, sr=sample_rate, win_length=cepstra_count
            )

    elif computation_source == "spectrogram":
        if chroma == "chromagram":
            # Compute from a power spectrogram
            S = np.abs(librosa.stft(y=vector, n_fft=n_fft, hop_length=window_size))
            return librosa.feature.chroma_stft(
                S=S,
                sr=sample_rate,
                norm=None,
                n_fft=n_fft,
                hop_length=window_size,
                n_chroma=cepstra_count,
            )

        elif chroma == "constantQ":
            # Compute from a constant-Q spectrogram
            C = np.abs(librosa.cqt(vector, sr=sample_rate))
            return librosa.feature.chroma_cqt(
                C=C, sr=sample_rate, n_chroma=cepstra_count, norm=False
            )

        elif chroma == "CENS":
            # Compute from a constant-Q spectrogram
            C = np.abs(librosa.cqt(vector, sr=sample_rate))
            return librosa.feature.chroma_cens(
                C=C, sr=sample_rate, n_chroma=cepstra_count, norm=False
            )

        elif chroma == "RMSE":
            # Compute from a spectrogram
            # !!! cepstra_count is used as a delta paramenter !!!
            S, phase = librosa.magphase(
                librosa.stft(vector, n_fft=n_fft, hop_length=cepstra_count)
            )
            return librosa.feature.rmse(
                S=S, frame_length=window_size, hop_length=cepstra_count
            )

        elif chroma == "spectral_cent":
            # Compute from a spectrogram
            S, phase = librosa.magphase(
                librosa.stft(vector, n_fft=n_fft, hop_length=window_size)
            )
            return librosa.feature.spectral_centroid(
                S=S, n_fft=n_fft, hop_length=window_size
            )

        elif chroma == "spectral_band":
            # Generate from spectrogram input
            S, phase = librosa.magphase(
                librosa.stft(vector, n_fft=n_fft, hop_length=window_size)
            )
            return librosa.feature.spectral_bandwidth(
                S=S, p=sample_rate, n_fft=n_fft, hop_length=window_size, norm=False
            )

        elif chroma == "spectral_cont":
            S = np.abs(librosa.stft(vector, n_fft=n_fft, hop_length=window_size))
            return librosa.feature.spectral_contrast(
                S=S,
                sr=sample_rate,
                n_fft=n_fft,
                hop_length=window_size,
                n_bands=params["number_of_bands"],
                fmin=params["frq_min"],
            )

        elif chroma == "spectral_flat":
            S, phase = librosa.magphase(
                librosa.stft(vector, n_fft=n_fft, hop_length=window_size)
            )
            return librosa.feature.spectral_flatness(
                S=S, n_fft=n_fft, hop_length=window_size
            )

        elif chroma == "spectral_roll":
            S, phase = librosa.magphase(
                librosa.stft(y=vector, n_fft=n_fft, hop_length=window_size)
            )
            return librosa.feature.spectral_rolloff(
                S=S,
                sr=sample_rate,
                roll_percent=params,
                n_fft=n_fft,
                hop_length=window_size,
            )

        elif chroma == "polynomial":
            S = np.abs(librosa.stft(y=vector, n_fft=n_fft, hop_length=window_size))
            return librosa.feature.poly_features(
                S=S, order=params, n_fft=n_fft, hop_length=window_size
            )
        elif chroma == "MFCCLib":
            S = librosa.feature.melspectrogram(
                y=vector, sr=sample_rate, n_fft=n_fft, hop_length=window_size
            )
            return librosa.feature.mfcc(S=librosa.power_to_db(S))

        elif chroma == "oenv":
            S = np.abs(librosa.stft(y=vector, n_fft=n_fft, hop_length=window_size))
            return [
                librosa.onset.onset_strength(
                    S=S, sr=sample_rate, hop_length=window_size
                )
            ]

        elif chroma == "tempogram":
            # variables are arranged intentially
            S = np.abs(librosa.stft(y=vector, n_fft=n_fft, hop_length=window_size))
            oenv = librosa.onset.onset_strength(
                S=S, sr=sample_rate, hop_length=window_size
            )
            return librosa.feature.tempogram(
                onset_envelope=oenv, sr=sample_rate, win_length=cepstra_count
            )

    else:
        raise InputParameterException("Selected computation_source is not supported.")


def chroma_function(
    input_data,
    input_columns,
    sample_rate,
    cepstra_count,
    window_size,
    computation_source,
    chroma,
    params=None,
):

    df_result = DataFrame([])
    for column in input_columns:
        vector = np.array(input_data[column].astype("float"))
        chroma_results = chroma_core(
            chroma,
            vector,
            sample_rate,
            512,
            window_size,
            cepstra_count,
            computation_source,
            params,
        )

        for c in range(len(chroma_results[0])):
            if chroma in [
                "RMSE",
                "spectral_cent",
                "spectral_band",
                "spectral_flat",
                "spectral_roll",
                "polynomial",
                "ZCRA",
                "oenv",
            ]:
                cepstra_str = "0000000" + str(c)
                feature_column = column + "_" + chroma + "_" + cepstra_str[-6:]
                df_result.loc[0, feature_column] = chroma_results[0][c]

            else:
                for cepstra in range(len(chroma_results)):
                    cepstra_str = "0000000" + str(cepstra)
                    feature_column = (
                        column
                        + "_CasWin"
                        + str(c)
                        + "_"
                        + chroma
                        + "_"
                        + cepstra_str[-6:]
                    )
                    df_result.loc[0, feature_column] = chroma_results[cepstra, c]

    return df_result


def chromagram(
    input_data,
    columns,
    sample_rate,
    cepstra_count,
    window_size,
    computation_source,
    group_columns,
):
    """
    Compute a chromagram from a waveform or power spectrogram.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        cepstra_count: <int> number of coefficients to generate
        window_size : <int> bin size of the signal
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of chromagram score of energy for each chroma bin at each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Chromagram',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "window_size": 400,
                                                            "cepstra_count": 23,
                                                            "computation_source": "waveform"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    return chroma_function(
        input_data,
        columns,
        sample_rate,
        cepstra_count,
        window_size,
        computation_source,
        "chromagram",
    )


chromagram_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "window_size", "type": "int"},
        {"name": "cepstra_count", "type": "int", "default": 23},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def chroma_energy_normalized(
    input_data, columns, sample_rate, cepstra_count, computation_source, group_columns
):
    """
    Computes the croma variant "Chroma Energy Normalized".

    Args:
        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        cepstra_count: <int> number of coefficients to generate
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of chromagram score of normilized energy for each chroma bin at each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Chroma Energy Normalized',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "cepstra_count": 23,
                                                            "computation_source": "waveform"}}])

        >>> r, s =  client.pipeline.execute(describe=False)

    """
    return chroma_function(
        input_data,
        columns,
        sample_rate,
        cepstra_count,
        None,
        computation_source,
        "CENS",
    )


chroma_energy_normalized_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "cepstra_count", "type": "int", "default": 23},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def constant_Q_chromagram(
    input_data, columns, sample_rate, cepstra_count, computation_source, group_columns
):
    """
    Compute a constant Q chromagram from a waveform or constant Q spectrum.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        cepstra_count: <int> number of coefficients to generate
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of chromagram Q score for each chroma bin at each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Constant Q Chromagram',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "cepstra_count": 23,
                                                            "computation_source": "waveform"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    return chroma_function(
        input_data,
        columns,
        sample_rate,
        cepstra_count,
        None,
        computation_source,
        "constantQ",
    )


constant_Q_chromagram_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "cepstra_count", "type": "int", "default": 23},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def root_mean_square(
    input_data, columns, window_size, delta, computation_source, group_columns
):
    """
    Compute root-mean-square (RMS) energy for each frame, either from the waveform or from a spectrogram S.
    Computing the energy from audio samples is faster. However, using a spectrogram will give a more accurate
    representation of energy over time.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        window_size : <int> bin size of the signal
        delta : <int> : number of samples overlap

        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Root Mean Square',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "window_size": 400,
                                                            "delta": 400,
                                                            "computation_source": "spectrogram"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    return chroma_function(
        input_data, columns, 0, delta, window_size, computation_source, "RMSE"
    )


root_mean_square_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "window_size", "type": "int"},
        {"name": "delta", "type": "int"},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def spectral_centroid(
    input_data, columns, sample_rate, window_size, computation_source, group_columns
):
    """
    Compute the spectral centroid. Each frame of a magnitude spectrogram is normalized and treated as a
    distribution over frequency bins, from which the mean (centroid) is extracted per frame.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        window_size : <int> bin size of the signal
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Spectral Centroid',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "window_size": 400,
                                                            "computation_source": "spectrogram"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    return chroma_function(
        input_data,
        columns,
        sample_rate,
        None,
        window_size,
        computation_source,
        "spectral_cent",
    )


spectral_centroid_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "window_size", "type": "int"},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def spectral_bandwidth(
    input_data, columns, p, window_size, computation_source, group_columns
):
    """
    Compute p'th order spectral bandwidth.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        p : <float> Power to raise derivation
        window_size : <int> bin size of the signal
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Spectral Bandwidth',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "window_size": 400,
                                                            "p": 2,
                                                            "computation_source": "spectrogram"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    # Using variable bin center frequencies can be added as a paramenter

    return chroma_function(
        input_data, columns, p, None, window_size, computation_source, "spectral_band"
    )


spectral_bandwidth_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "p", "type": "float"},
        {"name": "window_size", "type": "int"},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def spectral_contrast(
    input_data,
    columns,
    sample_rate,
    window_size,
    number_of_bands,
    frq_min,
    computation_source,
    group_columns,
):
    """
    Compute spectral_contrast

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        window_size : <int> bin size of the signal
        number_of_bands : Number of frequency bads
        frq_min : <int> Frequency cut off for the first bin
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Spectral Contrast',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "window_size": 400,
                                                            "number_of_bands": 5,
                                                            "frq_min": 200,
                                                            "computation_source": "spectrogram"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    # Using variable bin center frequencies can be added as a paramenter

    params = {"number_of_bands": number_of_bands, "frq_min": frq_min}
    return chroma_function(
        input_data,
        columns,
        sample_rate,
        number_of_bands,
        window_size,
        computation_source,
        "spectral_cont",
        params,
    )


spectral_contrast_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "window_size", "type": "int"},
        {"name": "number_of_bands", "type": "int", "default": 5},
        {"name": "frq_min", "type": "int", "default": 200},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def spectral_flatness(
    input_data, columns, window_size, computation_source, group_columns
):
    """
    Compute spectral flatness.
    Spectral flatness (or tonality coefficient) is a measure to quantify how much noise-like a sound is,
    as opposed to being tone-like [1]. A high spectral flatness (closer to 1.0) indicates the spectrum is
    similar to white noise. It is often converted to decibel.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        window_size : <int> bin size of the signal
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Spectral Flatness',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "window_size": 400,
                                                            "computation_source": "spectrogram"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    # Using variable bin center frequencies can be added as a paramenter

    return chroma_function(
        input_data,
        columns,
        None,
        None,
        window_size,
        computation_source,
        "spectral_flat",
    )


spectral_flatness_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "window_size", "type": "int"},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def spectral_rolloff(
    input_data,
    columns,
    sample_rate,
    window_size,
    roll_percent,
    computation_source,
    group_columns,
):
    """
    Compute spectral rolloff.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        cepstra_count: <int> number of coefficients to generate
        window_size : <int> bin size of the signal
        roll_percent: <int> Roll off percentage
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Spectral Rolloff',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "window_size": 400,
                                                            "roll_percent": 0.80,
                                                            "computation_source": "spectrogram"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """

    return chroma_function(
        input_data,
        columns,
        sample_rate,
        None,
        window_size,
        computation_source,
        "spectral_roll",
        params=roll_percent,
    )


spectral_rolloff_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "window_size", "type": "int"},
        {"name": "roll_percent", "type": "float", "default": 0.85},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def nth_order_polynomial(
    input_data,
    columns,
    sample_rate,
    window_size,
    order,
    computation_source,
    group_columns,
):
    """
    Get coefficients of fitting an nth-order polynomial to the columns of a spectrogram.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        cepstra_count: <int> number of coefficients to generate
        window_size : <int> bin size of the signal
        order : <int> order of the polynomial to fit
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Nth Order Polynomial',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "window_size": 400,
                                                            "order": 0,
                                                            "computation_source": "spectrogram"}}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """
    return chroma_function(
        input_data,
        columns,
        sample_rate,
        None,
        window_size,
        computation_source,
        "polynomial",
        params=order,
    )


nth_order_polynomial_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "window_size", "type": "int"},
        # , "default": 0,"options": [{"name": 1}, {"name": 2}, {"name": 3}]
        {"name": "order", "type": "int"},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def tonnetz(input_data, columns, sample_rate, margin, group_columns):
    """
    Computes the tonal centroid features (tonnetz).

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        margin : <float> harmonic seperation


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Tonnetz',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "margin": 2.0,
                                                            }}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """
    return chroma_function(
        input_data,
        columns,
        sample_rate,
        None,
        None,
        "waveform",
        "tonnetz",
        params=margin,
    )


tonnetz_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "margin", "type": "float"},
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def zero_crossing_rate_audio(input_data, columns, window_size, delta, group_columns):
    """
    Computes the zero crossing rate audio for each window size.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        window_size : <int> bin size of the signal
        delta : <int> : number of samples overlap


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Zero Crossing Rate Audio',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "window_size": 400,
                                                            "delta": 400,
                                                            }}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """
    return chroma_function(
        input_data, columns, None, None, window_size, "waveform", "ZCRA", params=delta
    )


zero_crossing_rate_audio_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "window_size", "type": "int"},
        {"name": "delta", "type": "int"},
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def volumeDB(input_data, columns, window_size, delta, group_columns):
    """
    Computes the decibel volume for each window.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        window_size : <int> bin size of the signal
        delta : <int> : number of samples overlap


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'VolumeDB',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "window_size": 400,
                                                            "delta": 400,
                                                            }}])

        >>> r, s =  client.pipeline.execute(describe=False)
    """

    wlen = len(input_data)
    if window_size == delta:
        step = window_size
    else:
        step = window_size - delta

    frameNum = int(math.ceil(wlen * 1.0 / step))
    np.zeros((window_size, 1))

    df_result = DataFrame([])
    for column in columns:
        vector = np.array(input_data[column])

        for c in range(frameNum):
            cepstra_str = "0000000" + str(c)
            feature_column = column + "_" + "volDB" + "_" + cepstra_str[-6:]
            curwind = vector[np.arange(c * step, min(c * step + window_size, wlen))]
            dmean = curwind - np.mean(curwind)
            df_result.loc[0, feature_column] = 10 * np.log10(np.sum(dmean * dmean))

    df_result = df_result.replace(-np.inf, 0)
    return df_result


volumeDB_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "window_size", "type": "int"},
        {"name": "delta", "type": "int"},
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def mFCC_lib(
    input_data,
    columns,
    sample_rate,
    cepstra_count,
    window_size,
    computation_source,
    group_columns,
):
    """
    Computes the MFCC for each window size.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        window_size : <int> bin size of the signal
        cepstra_count: <int> number of coefficients to generate
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'MFCCLib',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "cepstra_count": 23,
                                                            "window_size": 400,
                                                            "computation_source": "spectrogram"
                                                            }}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """
    return chroma_function(
        input_data,
        columns,
        sample_rate,
        cepstra_count,
        window_size,
        computation_source,
        "MFCCLib",
        params=None,
    )


mFCC_lib_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "cepstra_count", "type": "int", "default": 23},
        {"name": "window_size", "type": "int", "default": 400},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def onset_strength(
    input_data, columns, sample_rate, window_size, computation_source, group_columns
):
    """
    Compute a spectral flux onset strength envelope.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        window_size : <int> bin size of the signal
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram

    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Onset Strength',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "window_size": 400,
                                                            "computation_source": "spectrogram"
                                                            }}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """
    return chroma_function(
        input_data,
        columns,
        sample_rate,
        None,
        window_size,
        computation_source,
        "oenv",
        params=None,
    )


onset_strength_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "window_size", "type": "int"},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}


def tempogram(
    input_data,
    columns,
    sample_rate,
    window_size,
    cepstra_count,
    computation_source,
    group_columns,
):
    """
    Compute a spectral flux onset strength envelope.

    Args:

        input_data: <Dataframe>; input data
        columns: <List>; names of the sensor streams to use
        sample_rate : <int> sampling rate
        window_size : <int> bin size of the signal
        cepstra_count: <int> number of coefficients to generate
        computation_source : <str> define chromagram computation source. Options: waveform / spectrogram


    Returns:
        DataFrame of RMS values for each frame.

    Examples:
        >>> activity_data = client.datasets.load_activity_raw()
        >>> client.upload_dataframe('activity_data.csv', activity_data, force=True)
        >>> client.pipeline.reset(delete_cache=False)
        >>> client.pipeline.set_input_data('activity_data',
                                        data_columns = ['accelx', 'accely', 'accelz'],
                                        group_columns = ['Subject','Class'],
                                        label_column = 'Class')

        >>> client.pipeline.add_feature_generator([{'name':'Tempogram',
                                                 'params':{ "columns": ['accelx', 'accely', 'accelz'],
                                                            "sample_rate": 16000,
                                                            "window_size": 400,
                                                            "cepstra_count": 23,
                                                            "computation_source": "spectrogram"
                                                            }}])

        >>> r, s =  client.pipeline.execute(describe=False)


    """
    return chroma_function(
        input_data,
        columns,
        sample_rate,
        cepstra_count,
        window_size,
        computation_source,
        "tempogram",
        params=None,
    )


tempogram_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sample_rate", "type": "int"},
        {"name": "window_size", "type": "int"},
        {"name": "cepstra_count", "type": "int"},
        {
            "name": "computation_source",
            "type": "str",
            "default": "waveform",
            "options": [{"name": "waveform"}, {"name": "spectrogram"}],
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}
