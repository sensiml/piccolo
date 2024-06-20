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
import tempfile
from uuid import uuid4

import pytest
from datamanager.utils.file_reader import CSVFileReader, WaveFileReader
from pandas import DataFrame, read_csv


@pytest.fixture
def filereader_float():
    """Creates test files and yields to test before cleaning up"""

    path = os.path.join(tempfile.gettempdir(), "%s.csv" % uuid4().hex)
    with open(path, "w+") as f:
        f.write(
            "AccelerometerX,AccelerometerY,GyroscopeZ\n1.2,2.3,7.34\n9.3,4.0,12.43\n44,34.5,0.0001"
        )

    yield CSVFileReader(path)

    os.remove(path)


@pytest.fixture
def filereader_mixed_int_float():
    """Creates test files and yields to test before cleaning up"""

    path = os.path.join(tempfile.gettempdir(), "%s.csv" % uuid4().hex)
    with open(path, "w+") as f:
        f.write(
            "AccelerometerX,AccelerometerY,GyroscopeZ\n1,2,7\n9,4.0,12.43\n44,34.5,0.0001"
        )

    yield CSVFileReader(path)

    os.remove(path)


@pytest.fixture
def filereader_int():
    """Creates test files and yields to test before cleaning up"""

    path = os.path.join(tempfile.gettempdir(), "%s.csv" % uuid4().hex)
    with open(path, "w+") as f:
        f.write("AccelerometerX,AccelerometerY,GyroscopeZ\n1,2,7\n9,4,12\n44,34,0")

    yield CSVFileReader(path)

    os.remove(path)


@pytest.fixture
def filereader_int_bad_fields():
    """Creates test files and yields to test before cleaning up"""

    path = os.path.join(tempfile.gettempdir(), "%s.csv" % uuid4().hex)
    with open(path, "w+") as f:
        f.write("Accelerometer!X,AccelerometerY,GyroscopeZ\n1,2,7\n9,4,12\n44,34,0")

    yield path

    os.remove(path)


@pytest.fixture
def filereader_int_name_space_fields():
    """Creates test files and yields to test before cleaning up"""

    path = os.path.join(tempfile.gettempdir(), "%s.csv" % uuid4().hex)
    with open(path, "w+") as f:
        f.write("Accelerometer X,AccelerometerY,GyroscopeZ\n1,2,7\n9,4,12\n44,34,0")

    yield CSVFileReader(path)

    os.remove(path)


def test_csv_reader_data(filereader_float):
    data = DataFrame(
        [[1.2, 2.3, 7.34], [9.3, 4.0, 12.43], [44, 34.5, 0.0001]],
        columns=["AccelerometerX", "AccelerometerY", "GyroscopeZ"],
    ).to_dict(orient="record")
    filereader_float._dataframe.equals(data)


def test_csv_reader_data_mixed(filereader_mixed_int_float):
    data = DataFrame(
        [[1, 2, 7], [9.3, 4.0, 12.43], [44, 34.5, 0.0001]],
        columns=["AccelerometerX", "AccelerometerY", "GyroscopeZ"],
    ).to_dict(orient="record")
    filereader_mixed_int_float._dataframe.equals(data)


def test_csv_reader_schema_int_float(filereader_mixed_int_float):
    schema = filereader_mixed_int_float.schema
    assert {
        "AccelerometerX": {"type": "int", "index": 0},
        "AccelerometerY": {"type": "float", "index": 1},
        "GyroscopeZ": {"type": "float", "index": 2},
    } == schema


def test_csv_reader_schema_float(filereader_float):
    schema = filereader_float.schema
    assert {
        "AccelerometerX": {"type": "float", "index": 0},
        "AccelerometerY": {"type": "float", "index": 1},
        "GyroscopeZ": {"type": "float", "index": 2},
    } == schema


def test_csv_reader_schema_int(filereader_int):
    schema = filereader_int.schema
    assert {
        "AccelerometerX": {"type": "int", "index": 0},
        "AccelerometerY": {"type": "int", "index": 1},
        "GyroscopeZ": {"type": "int", "index": 2},
    } == schema


def test_csv_reader_schema_int_space_fields(filereader_int_name_space_fields):
    schema = filereader_int_name_space_fields.schema
    assert {
        "Accelerometer_X": {"type": "int", "index": 0},
        "AccelerometerY": {"type": "int", "index": 1},
        "GyroscopeZ": {"type": "int", "index": 2},
    } == schema


def test_csv_reader_validation_fails(filereader_int_bad_fields):

    failed = False
    try:
        CSVFileReader(filereader_int_bad_fields)
    except Exception as e:
        assert (
            str(e)
            == 'Value "Accelerometer!X" can only contain letters, numbers and underscores and spaces.'
        )
        failed = True

    assert failed


def test_csv_reader_non_numeric_error():
    """Creates test files and yields to test before cleaning up"""

    path = os.path.join(tempfile.gettempdir(), "%s.csv" % uuid4().hex)
    with open(path, "w+") as f:
        f.write(
            "AccelerometerX,AccelerometerY,GyroscopeZ\n1.2,2.3,7.34\n9.3,string,12.43\n44,34.5,0.0001"
        )

    try:
        CSVFileReader(path)
        failed = False
    except Exception as e:
        failed = True
        assert (
            str(e)
            == "Invalid values in column(s) AccelerometerY. All columns must contain only numeric data."
        )

    if not failed:
        assert False


def test_wave_reader_2_channel():
    """Creates test files and yields to test before cleaning up"""

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/2channel.wav")

    wfr = WaveFileReader(path)

    assert list(wfr._dataframe.columns) == ["channel_0", "channel_1"]
    assert wfr._dataframe.shape == (112, 2)

    tmp_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data/tmp_2channel.wav"
    )

    wfr.to_CSVFileReader(tmp_path)
    read_csv(tmp_path)

    assert list(wfr._dataframe.columns) == ["channel_0", "channel_1"]
    assert wfr._dataframe.shape == (112, 2)

    os.remove(tmp_path)
