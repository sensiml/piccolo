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

import heapq
import math

from numpy import (
    argmax,
    array,
    ceil,
    concatenate,
    corrcoef,
    cumsum,
    dot,
    linalg,
    mean,
    pi,
    real,
    sqrt,
    square,
    trapz,
)
from pandas import DataFrame
from scipy.fftpack import dct, fft


def theta_est(theta_dot, sample_rate=128):
    """Estimates angular displacement (rad) from angular velocity (rad/sec).

    Input:
        theta_dot: angular velocity
    Output:
        theta: angular displacement
    """

    theta_dot = abs(theta_dot)
    # Subtract mean to avoid choosing DC component
    theta_dot_fft = abs(fft(theta_dot - mean(theta_dot)))
    l = round(len(theta_dot_fft) / float(2))
    theta_dot_fft = theta_dot_fft[:l]  # Remove mirror spectrum
    # Return dominant frequency f_peak (NOT f_max!!)
    f_peak = argmax(theta_dot_fft)

    # T_theta = 1/(float(f_peak))
    # T_theta = round(T_theta*128)      # Scaling period by sampling rate to get period in seconds
    T_theta = round(sample_rate / (float(f_peak)))

    if T_theta > len(theta_dot):
        # Avoiding errors when calculated period is longer than available waveform
        T_theta = len(theta_dot)
    # Integrate over period to get angular displacement in radians:
    theta = (1 / float(sample_rate)) * trapz(
        theta_dot[range(int(T_theta))], x=None, dx=1
    )
    # Might be better to shift integration interval to center), keep scalar 1/128 out of integral not in dx
    theta = 180 - theta * (180 / float(pi))  # Theta in degrees!
    return theta


def d_est(acc, sample_rate=128):
    """Estimates Cartesian displacement (m) from acceleration (m/sec^2).

    Input:
        acc - accelerometer signal
    Output:
        d - linear displacement
    """

    acc = abs(acc)
    # subtract mean to avoid choosing DC component
    acc_fft = abs(fft(acc - mean(acc)))
    l = round(len(acc_fft) / float(2))
    acc_fft = acc_fft[:l]  # Remove mirror spectrum
    f_peak = argmax(acc_fft)  # Return dominant frequency f_peak (NOT f_max!!)
    # Reciprocal of frequency is halved to focus on half cycle
    T_acc = 1 / (float(f_peak))
    # Scaling period by sampling rate to get period in seconds
    T_acc = round(T_acc * sample_rate)
    if T_acc > len(acc):
        # Avoiding errors when calculated period is longer than available waveform
        T_acc = len(acc)
    # integrating over period to get andular displacment in radians
    d = (1 / float(sample_rate)) ** 2 * trapz(
        cumsum(acc[range(int(T_acc))]), x=None, dx=1
    )
    # might be better to shift integration interval to center), keep scalar 1/128 out of integral not in dx
    return d


def cart2sph(x, y, z):
    """Converts Cartesian coordinates to spherical coordinates.

    Input:
        x,y,z - data from x, y, and z axes - cartesian co-ordinates
    Output:
        r, theta, phi - spherical co-ordinates
    """

    rho = x ** 2 + y ** 2
    r = math.sqrt(rho + z ** 2)
    theta = math.atan2(z, math.sqrt(rho))
    phi = math.atan2(y, x)
    return r, theta, phi


def CSCC(x, m, q, p):
    """Computes the first cepstral coefficients of a temporal waveform based on
    overlapping triangular window functions.

    Inputs:
        x: Temporal waveform
        m: Number of triangular windows
        q: Number of desired coefficients (takes values from 0 to q-1), should be strictly and significantly less than len(x)
        p: Percentage of overlap between triangular windows
    Outputs:
        CSCC: a q-dimensional array of CSCC
    """

    L = int(ceil(len(x) / float(m)))
    # Computing length of triangular window with p% overlap
    Lm = int(ceil(L * (1 - p / float(100))))

    ind_L = range(1, L)
    # Computing Fourier coefficents to collect PSD coefficents
    x_f = abs(fft(x))
    p_f = [k ** 2 for k in x_f]  # Power Spectral Density of x

    t1 = range(0, L / 2)
    w1 = []
    w2 = []
    # First half of triangular window function
    w1 = [k * (2 / float(L)) for k in t1]
    # Second half of triangular window function
    w2 = [1 + k * (-2 / float(L)) for k in t1]
    w = concatenate([w1, w2])
    w = w[0:-1]

    E_f_w = []
    # Sliding overlapped window function, multiplying by corresponding PSD of x, and summing (i.e. dot product)
    for i in range(1, m + 1):
        ind_range = range((i - 1) * Lm + min(ind_L) + 1, (i - 1) * Lm + max(ind_L) + 1)
        p_f_w = [p_f[k] for k in ind_range]
        if len(p_f_w) < len(w):  # Avoiding mismatch in length of p_f_W and w blocks
            w = w[0 : len(p_f_w)]
        elif len(p_f_w) > len(w):
            # Avoiding mismatch in length of p_f_W and w blocks
            p_f_w = p_f_w[0 : len(w)]

        # Dot product of overlapped window and corresponding PSD
        E_f_w.append(dot(w, p_f_w))
        # Computing Discrete Cosine Coefficients of the (overlapped) dot product between PSD and window function, these will be the complete CSCC coefficients
        CSCC = dct(E_f_w, 2)
        CSCC = abs(CSCC[0 : q - 1])  # Taking the first q such coefficients

    return CSCC


def magnitude(input_data, input_columns):
    """Computes the magnitude of each column in a dataframe"""
    return sqrt(square(input_data[input_columns]).sum(axis=1))


def average_movement_intensity(input_data, columns, **kwargs):
    """
    Average of movement intensity

    Args:
        input_data: input DataFrame.
        columns:  List of str; The `columns` represents a list of all column
            names on which `are` is to be found.
        group_columns: List of str; Set of columns by which to aggregate

    Returns:
        DataFrame

    """
    results = {}

    norm_data = magnitude(input_data, columns)

    # Feature: average Intensity of instantaneous movement intensity
    results["AvgInt"] = norm_data.sum() / float(len(norm_data))

    return DataFrame.from_dict(results)


average_movement_intensity_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def variance_movement_intensity(input_data, columns, **kwargs):
    """
    Variance of movement intensity

    Args:
        input_data: input DataFrame.
        columns:  List of str; The `columns` represents a list of all column
          names on which `variance_movement_intensity` is to be found.
        group_columns: List of str; Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20,
                               'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    0     s01       1       0       1
                1   Crawling    0     s01      -2       9      -2
                2   Crawling    0     s01      -3       5       3
                3   Crawling    0     s01       1      -5      -1
                4   Crawling    0     s01       2      -9       2
                5   Crawling    0     s01       5       0       5
                6   Crawling    0     s01       2       9       2
                7   Crawling    0     s01      -2       5      -2
                8   Crawling    1     s01      -3      -5      -3
                9   Crawling    1     s01      -1      -9       1
                10  Crawling    1     s01       1       0       1
                11  Crawling    1     s01      -3       9       3
                12  Crawling    1     s01      -4       5       4
                13  Crawling    1     s01       1      -5       1
                14  Crawling    1     s01       2      -9       2
                15  Crawling    1     s01       6       0       6
                16  Crawling    1     s01       2       9       2
                17  Crawling    1     s01      -3       5      -3
                18  Crawling    1     s01      -2      -5      -2
                19  Crawling    1     s01      -1      -9      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Variance of Movement Intensity"],
             params = {"group_columns": ['Subject', 'Class', 'Rep']},
                        function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0000_VarInt
            0  Crawling    0     s01         6.704651
            1  Crawling    1     s01         5.555739
    """
    results = {}

    norm_data = magnitude(input_data, columns)

    # Feature: variance intensity of inst. movement intensity
    AI = (1 / float(len(norm_data))) * norm_data.sum()
    VI = (1 / float(len(norm_data))) * sum((norm_data - AI) ** 2)

    results["VarInt"] = [VI]

    return DataFrame.from_dict(results)


variance_movement_intensity_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def average_signal_magnitude_area(input_data, columns, **kwargs):
    """
    Average signal magnitude area (average energy of movement intensity)

    Args:
        input_data: input DataFrame.
        columns:  List of str; The `columns` represents a list of all column
          names on which `average_signal_magnitude_area` is to be found.
        group_columns: List of str; Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                              'Class': ['Crawling'] * 20,
                              'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    0     s01       1       0       1
                1   Crawling    0     s01      -2       9      -2
                2   Crawling    0     s01      -3       5       3
                3   Crawling    0     s01       1      -5      -1
                4   Crawling    0     s01       2      -9       2
                5   Crawling    0     s01       5       0       5
                6   Crawling    0     s01       2       9       2
                7   Crawling    0     s01      -2       5      -2
                8   Crawling    1     s01      -3      -5      -3
                9   Crawling    1     s01      -1      -9       1
                10  Crawling    1     s01       1       0       1
                11  Crawling    1     s01      -3       9       3
                12  Crawling    1     s01      -4       5       4
                13  Crawling    1     s01       1      -5       1
                14  Crawling    1     s01       2      -9       2
                15  Crawling    1     s01       6       0       6
                16  Crawling    1     s01       2       9       2
                17  Crawling    1     s01      -3       5      -3
                18  Crawling    1     s01      -2      -5      -2
                19  Crawling    1     s01      -1      -9      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["Average Signal Magnitude Area (Average Energy of Movement Intensity)"],
                 params = {"group_columns": ['Subject', 'Class', 'Rep']},
                 function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0000_AvgSigMag
            0  Crawling    0     s01            9.750000
            1  Crawling    1     s01           10.666667
    """

    results = {}

    # Convert to numpy arrays for faster iteration
    abs_sum = input_data[columns].abs().sum(axis=1).sum(axis=0)

    # Feature: normalized signal magnitude area
    SMA = (1 / float(len(input_data))) * (abs_sum)

    results["AvgSigMag"] = [SMA]

    return DataFrame.from_dict(results)


average_signal_magnitude_area_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def dominant_direction_linear(input_data, columns, **kwargs):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "columns", "type": "list", "element_type": "str", "description": "Set of columns on which to apply the feature generator"},
    {"name": "group_columns", "type": "list", "element_type": "str", "handle_by_set": true, "description": "Set of columns by which to aggregate"}],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "costs": [{"name": "RAM", "value": 1.53}, {"name": "Flash", "value": 0.57}, {"name": "Clocks", "value": 1.91}],

    "description": "Dominant direction of linear velocity."
    }
    """
    if len(columns) != 3:
        raise Exception("Not enough input columns")

    results = {}
    results["LambdaMaxA"] = []

    # Convert to numpy arrays for faster iteration
    x_a = array(input_data[columns[0]]).T
    y_a = array(input_data[columns[1]]).T
    z_a = array(input_data[columns[2]]).T

    # Form 3xn matrices in order to compute principal components
    Xa = [x_a, y_a, z_a]
    Xa_np = (array(Xa)).T

    # Compute eigenvalues of data covariance matrices
    lambdas_a = real(linalg.eigvals(dot(Xa_np.T, Xa_np)))

    # Collect maximum eigenvalue
    lambda_max_a = heapq.nlargest(1, lambdas_a)[0]
    results["LambdaMaxA"].append(lambda_max_a)

    return DataFrame.from_dict(results)


def second_direction_linear(input_data, columns, **kwargs):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "columns", "type": "list", "element_type": "str", "description": "Set of columns on which to apply the feature generator"},
    {"name": "group_columns", "type": "list", "element_type": "str", "handle_by_set": true, "description": "Set of columns by which to aggregate"}],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "costs": [{"name": "RAM", "value": 0.69}, {"name": "Flash", "value": 0.32}, {"name": "Clocks", "value": 3.0}],

    "description": "Second direction of linear velocity."
    }
    """
    if len(columns) != 3:
        raise Exception("Not enough input columns")

    results = {}
    results["Lambda2ndA"] = []

    # Convert to numpy arrays for faster iteration
    x_a = array(input_data[columns[0]]).T
    y_a = array(input_data[columns[1]]).T
    z_a = array(input_data[columns[2]]).T

    # Form 3xn matrices in order to compute principle components
    Xa = [x_a, y_a, z_a]
    Xa_np = (array(Xa)).T

    # Compute eigenvalues of data covariance matrices
    lambdas_a = real(linalg.eigvals(dot(Xa_np.T, Xa_np)))

    # Collect second maximum eigenvalue
    lambda_2nd_a = heapq.nlargest(2, lambdas_a)[1]
    results["Lambda2ndA"].append(lambda_2nd_a)

    return DataFrame.from_dict(results)


def dominant_direction_angular(input_data, columns, **kwargs):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "columns", "type": "list", "element_type": "str", "description": "Set of columns on which to apply the feature generator"},
    {"name": "group_columns", "type": "list", "element_type": "str", "handle_by_set": true, "description": "Set of columns by which to aggregate"}],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "costs": [{"name": "RAM", "value": 3.98}, {"name": "Flash", "value": 0.24}, {"name": "Clocks", "value": 1.1}],

    "description": "Dominant direction of angular velocity."
    }
    """
    if len(columns) != 3:
        raise Exception("Not enough input columns")

    results = {}
    results["LambdaMaxG"] = []

    # Convert to numpy arrays for faster iteration
    x_g = array(input_data[columns[0]]).T
    y_g = array(input_data[columns[1]]).T
    z_g = array(input_data[columns[2]]).T

    # Form 3xn matrices in order to compute principle components
    Xg = [x_g, y_g, z_g]
    Xg_np = (array(Xg)).T

    # Compute eigenvalues of data covariance matrix
    lambdas_g = real(linalg.eigvals(dot(Xg_np.T, Xg_np)))

    # Collect maximum eigenvalue
    lambda_max_g = heapq.nlargest(1, lambdas_g)[0]
    results["LambdaMaxG"].append(lambda_max_g)

    return DataFrame.from_dict(results)


def second_direction_angular(input_data, columns, **kwargs):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "columns", "type": "list", "element_type": "str", "description": "Set of columns on which to apply the feature generator"},
    {"name": "group_columns", "type": "list", "element_type": "str", "handle_by_set": true, "description": "Set of columns by which to aggregate"}],

    "post": [
    {"name": "output_data", "type": "DataFrame"}],

    "costs": [{"name": "RAM", "value": 1.56}, {"name": "Flash", "value": 0.48}, {"name": "Clocks", "value": 0.71}],

    "description": "Second direction of angular velocity."
    }
    """
    if len(columns) != 3:
        raise Exception("Not enough input columns")

    results = {}
    results["Lambda2ndG"] = []

    # Convert to numpy arrays for faster iteration
    x_g = array(input_data[columns[0]]).T
    y_g = array(input_data[columns[1]]).T
    z_g = array(input_data[columns[2]]).T

    # Form 3xn matrices in order to compute principle components
    Xg = [x_g, y_g, z_g]
    Xg_np = (array(Xg)).T

    # Compute eigenvalues of data covariance matrices
    lambdas_g = real(linalg.eigvals(dot(Xg_np.T, Xg_np)))

    # Collect second maximum eigenvalue
    lambda_2nd_g = heapq.nlargest(2, lambdas_g)[1]
    results["Lambda2ndG"].append(lambda_2nd_g)

    return DataFrame.from_dict(results)


def cagh(input_data, columns, **kwargs):
    """
    CAGH - Correlation of linear acceleration between gravity and heading direction.

    Args:
        input_data: input DataFrame.
        columns:  List of str; The `columns` represents a list of all
            column names on which `cagh` is to be found.
        group_columns: List of str; Set of columns by which to aggregate

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                             'Class': ['Crawling'] * 20,
                             'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2, -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    0     s01       1       0       1
                1   Crawling    0     s01      -2       9      -2
                2   Crawling    0     s01      -3       5       3
                3   Crawling    0     s01       1      -5      -1
                4   Crawling    0     s01       2      -9       2
                5   Crawling    0     s01       5       0       5
                6   Crawling    0     s01       2       9       2
                7   Crawling    0     s01      -2       5      -2
                8   Crawling    1     s01      -3      -5      -3
                9   Crawling    1     s01      -1      -9       1
                10  Crawling    1     s01       1       0       1
                11  Crawling    1     s01      -3       9       3
                12  Crawling    1     s01      -4       5       4
                13  Crawling    1     s01       1      -5       1
                14  Crawling    1     s01       2      -9       2
                15  Crawling    1     s01       6       0       6
                16  Crawling    1     s01       2       9       2
                17  Crawling    1     s01      -3       5      -3
                18  Crawling    1     s01      -2      -5      -2
                19  Crawling    1     s01      -1      -9      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["CAGH - Correlation of Linear Acceleration between Gravity and Heading Direction"],
                    params = {"group_columns": ['Subject', 'Class', 'Rep']},
                    function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  Class  Rep Subject  gen_0000_CAGH
            0  Crawling    0     s01       0.252282
            1  Crawling    1     s01      -0.144809
    Notes:
        Zhang, Mi, and Alexander A. Sawchuk. "Motion primitive-based human activity recognition
        using a bag-of-features approach."  Proceedings of the 2nd ACM SIGHIT International
        Health Informatics Symposium. ACM, 2012.
    """
    if len(columns) != 3:
        raise Exception("Not enough input columns")

    results = {}
    results["CAGH"] = []
    v_norm = []
    h_norm = []

    # Convert to numpy arrays for faster iteration
    x_a = array(input_data[columns[0]]).T
    y_a = array(input_data[columns[1]]).T
    z_a = array(input_data[columns[2]]).T

    # Estimate acceleration component along gravity direction
    G = [mean(x_a), mean(y_a), mean(z_a)]

    # Movement intensity: instantaneous Euclidean norm of acceleration vector
    for j in range(len(x_a)):
        a = [x_a[j], y_a[j], z_a[j]]

        # Estimate instantaneous acceleration component (norm) along gravity direction
        v = dot(a, G)
        v_norm.append(v)

        # Take orthogonal complement of v to estimate heading direction
        h = a - v * array(G / linalg.norm(G))
        # Norm of orthogonal complement
        h_norm.append(linalg.norm(h))

    # Feature: correlation matrix of acceleration along gravity and heading directions
    CAGH = corrcoef(v_norm, h_norm)
    # Want diagonal element of correlation matrix corresponding to the correlation coefficient
    results["CAGH"].append(CAGH[0, 1])

    return DataFrame.from_dict(results)


cagh_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def aratg(input_data, columns, **kwargs):
    """
    ARATG - Average angle of rotation in the direction of gravity
    Must have at least four columns. Always looking for 4th column in the columns list

    Args:
        input_data: input DataFrame.
        columns:  List of str; The `columns` represents a list of all column
          names on which `aratg` is to be found.
        group_columns: List of str; Set of columns by which to aggregate
        **kwargs:

    Returns:
        DataFrame

    Examples:
        >>> df = pd.DataFrame({'Subject': ['s01'] * 20,
                               'Class': ['Crawling'] * 20,
                               'Rep': [0] * 8 + [1] * 12})
        >>> df['accelx'] = [1, -2, -3, 1, 2, 5, 2, -2, -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1]
        >>> df['accely'] = [0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9]
        >>> df['accelz'] = [1, -2, 3, -1, 2, 5, 2, -2,-3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1]
        >>> df
            out:
                       Class  Rep Subject  accelx  accely  accelz
                0   Crawling    0     s01       1       0       1
                1   Crawling    0     s01      -2       9      -2
                2   Crawling    0     s01      -3       5       3
                3   Crawling    0     s01       1      -5      -1
                4   Crawling    0     s01       2      -9       2
                5   Crawling    0     s01       5       0       5
                6   Crawling    0     s01       2       9       2
                7   Crawling    0     s01      -2       5      -2
                8   Crawling    1     s01      -3      -5      -3
                9   Crawling    1     s01      -1      -9       1
                10  Crawling    1     s01       1       0       1
                11  Crawling    1     s01      -3       9       3
                12  Crawling    1     s01      -4       5       4
                13  Crawling    1     s01       1      -5       1
                14  Crawling    1     s01       2      -9       2
                15  Crawling    1     s01       6       0       6
                16  Crawling    1     s01       2       9       2
                17  Crawling    1     s01      -3       5      -3
                18  Crawling    1     s01      -2      -5      -2
                19  Crawling    1     s01      -1      -9      -1
        >>> client.pipeline.reset()
        >>> client.pipeline.set_input_data('test_data', df, force=True)
        >>> client.pipeline.add_feature_generator(["ARATG - Average Angle of Rotation in the Direction of Gravity"],
                params = {"group_columns": ['Subject', 'Class', 'Rep']},
                function_defaults={"columns":['accelx', 'accely', 'accelz']})
        >>> result, stats = client.pipeline.execute()
        >>> print result
            out:
                  ARATG     Class  Rep Subject
            0  1.000000  Crawling    0     s01
            1  0.916667  Crawling    1     s01
    Notes:
        Zhang, Mi, and Alexander A. Sawchuk. "Motion primitive-based human
        activity recognition using a bag-of-features approach." Proceedings
        of the 2nd ACM SIGHIT International Health Informatics Symposium. ACM, 2012.
    """
    if len(columns) != 3:
        raise Exception("Not enough input columns")

    results = {}
    results["ARATG"] = []

    # Convert to numpy array for faster iteration
    x_g = array(input_data[columns[0]]).T

    # Feature: average rotation angle related to gravity direction
    ARATG = sum(x_g) / float(len(x_g))
    results["ARATG"].append(ARATG)

    return DataFrame.from_dict(results)


aratg_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Set of columns on which to apply the feature generator",
        },
        {
            "name": "group_columns",
            "type": "list",
            "element_type": "str",
            "handle_by_set": True,
            "description": "Set of columns by which to aggregate",
        },
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame"}],
}


def angular_displacement(input_data, columns, sample_rate, **kwargs):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "columns", "type": "list", "element_type": "str", "description": "Set of columns on which to apply the feature generator"},
    {"name": "sample_rate", "type": "int", "handle_by_set": true, "description": "Sample rate of the sensor data"},
    {"name": "group_columns", "type": "list", "element_type": "str", "handle_by_set": true, "description": "Set of columns by which to aggregate"}],
    "post": [
    {"name": "output_data", "type": "DataFrame"}],
    "costs": [{"name": "RAM", "value": 1.76}, {"name": "Flash", "value": 0.16}, {"name": "Clocks", "value": 4.5}],
    "description": "Angular displacement in both Angular and Cartesian coordinate system ."
    }
    """
    if len(columns) != 6:
        raise Exception("Not enough input columns")

    results = {}
    results["XTheta"] = []
    results["YTheta"] = []
    results["ZTheta"] = []
    results["R"] = []
    results["Theta"] = []
    results["Phi"] = []

    # Convert to numpy array for faster iteration
    x_a = array(input_data[columns[0]]).T
    y_a = array(input_data[columns[1]]).T
    z_a = array(input_data[columns[2]]).T
    x_g = array(input_data[columns[3]]).T
    y_g = array(input_data[columns[4]]).T
    z_g = array(input_data[columns[5]]).T

    # Cartesian coordinates
    # Feature: estimate of angular displacement along x-component (gyro)
    x_theta = theta_est(x_g, sample_rate)
    # Feature: estimate of angular displacement along y-component (gyro)
    y_theta = theta_est(y_g, sample_rate)
    # Feature: estimate of angular displacement along z-component (gyro)
    z_theta = theta_est(z_g, sample_rate)

    # Polar coordinates
    # Estimate of linear displacement along x-axis (accelerometer)
    x_disp = d_est(x_a, sample_rate)
    # Estimate of linear displacement along y-axis (accelerometer)
    y_disp = d_est(y_a, sample_rate)
    # Estimate of linear displacement along z-axis (accelerometer)
    z_disp = d_est(z_a, sample_rate)
    # Features: estimate of angular displacement along xyz-components (gyro)
    r, theta, phi = cart2sph(x_disp, y_disp, z_disp)

    results["XTheta"].append(x_theta)
    results["YTheta"].append(y_theta)
    results["ZTheta"].append(z_theta)
    results["R"].append(r)
    results["Theta"].append(theta)
    results["Phi"].append(phi)

    return DataFrame.from_dict(results)


def cscc(input_data, columns, **kwargs):
    """
    {"pre": [
    {"name": "input_data", "type": "DataFrame"},
    {"name": "columns", "type": "list", "element_type": "str", "description": "Set of columns on which to apply the feature generator"},
    {"name": "group_columns", "type": "list", "element_type": "str", "handle_by_set": true,"description": "Set of columns by which to aggregate"}],
    "post": [
    {"name": "output_data", "type": "DataFrame"}],
    "costs": [{"name": "RAM", "value": 2.79}, {"name": "Flash", "value": 0.68}, {"name": "Clocks", "value": 2.41}],
    "description": "Compressed Subband Cepstral Coefficients."
    }
    """
    if len(columns) != 6:
        raise Exception("Not enough input columns")

    results = {}
    results["CSCC_XA1"] = []
    results["CSCC_XA2"] = []
    results["CSCC_XA3"] = []
    results["CSCC_XA4"] = []
    results["CSCC_YA1"] = []
    results["CSCC_YA2"] = []
    results["CSCC_YA3"] = []
    results["CSCC_YA4"] = []
    results["CSCC_ZA1"] = []
    results["CSCC_ZA2"] = []
    results["CSCC_ZA3"] = []
    results["CSCC_ZA4"] = []
    results["CSCC_XG1"] = []
    results["CSCC_XG2"] = []
    results["CSCC_XG3"] = []
    results["CSCC_XG4"] = []
    results["CSCC_YG1"] = []
    results["CSCC_YG2"] = []
    results["CSCC_YG3"] = []
    results["CSCC_YG4"] = []
    results["CSCC_ZG1"] = []
    results["CSCC_ZG2"] = []
    results["CSCC_ZG3"] = []
    results["CSCC_ZG4"] = []

    # Convert to numpy array for faster iteration
    x_a = array(input_data[columns[0]]).T
    y_a = array(input_data[columns[1]]).T
    z_a = array(input_data[columns[2]]).T
    x_g = array(input_data[columns[3]]).T
    y_g = array(input_data[columns[4]]).T
    z_g = array(input_data[columns[5]]).T

    if int(ceil(len(x_a) / float(10))) > 1:
        # Feature(s): CSCC coefficients of accelerometer sample function along x-axis
        CSCC_x_a = CSCC(x_a, 10, 5, 50)
        # Feature(s): CSCC coefficients of accelerometer sample function along y-axis
        CSCC_y_a = CSCC(y_a, 10, 5, 50)
        # Feature(s): CSCC coefficients of accelerometer sample function along z-axis
        CSCC_z_a = CSCC(z_a, 10, 5, 50)
        # Feature(s): CSCC coefficients of gyro sample function along x-axis
        CSCC_x_g = CSCC(x_g, 10, 5, 50)
        # Feature(s): CSCC coefficients of gyro sample function along y-axis
        CSCC_y_g = CSCC(y_g, 10, 5, 50)
        # Feature(s): CSCC coefficients of gyro sample function along z-axis
        CSCC_z_g = CSCC(z_g, 10, 5, 50)
    else:
        CSCC_x_a = [0, 0, 0, 0]
        CSCC_y_a = [0, 0, 0, 0]
        CSCC_z_a = [0, 0, 0, 0]
        CSCC_x_g = [0, 0, 0, 0]
        CSCC_y_g = [0, 0, 0, 0]
        CSCC_z_g = [0, 0, 0, 0]

    results["CSCC_XA1"].append(CSCC_x_a[0])
    results["CSCC_XA2"].append(CSCC_x_a[1])
    results["CSCC_XA3"].append(CSCC_x_a[2])
    results["CSCC_XA4"].append(CSCC_x_a[3])
    results["CSCC_YA1"].append(CSCC_y_a[0])
    results["CSCC_YA2"].append(CSCC_y_a[1])
    results["CSCC_YA3"].append(CSCC_y_a[2])
    results["CSCC_YA4"].append(CSCC_y_a[3])
    results["CSCC_ZA1"].append(CSCC_z_a[0])
    results["CSCC_ZA2"].append(CSCC_z_a[1])
    results["CSCC_ZA3"].append(CSCC_z_a[2])
    results["CSCC_ZA4"].append(CSCC_z_a[3])
    results["CSCC_XG1"].append(CSCC_x_g[0])
    results["CSCC_XG2"].append(CSCC_x_g[1])
    results["CSCC_XG3"].append(CSCC_x_g[2])
    results["CSCC_XG4"].append(CSCC_x_g[3])
    results["CSCC_YG1"].append(CSCC_y_g[0])
    results["CSCC_YG2"].append(CSCC_y_g[1])
    results["CSCC_YG3"].append(CSCC_y_g[2])
    results["CSCC_YG4"].append(CSCC_y_g[3])
    results["CSCC_ZG1"].append(CSCC_z_g[0])
    results["CSCC_ZG2"].append(CSCC_z_g[1])
    results["CSCC_ZG3"].append(CSCC_z_g[2])
    results["CSCC_ZG4"].append(CSCC_z_g[3])

    return DataFrame.from_dict(results)
