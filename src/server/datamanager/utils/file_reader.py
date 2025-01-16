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

import csv
import logging
import re
import wave

import numpy as np
from datamanager.exceptions import BadCaptureSchemaError
from pandas import DataFrame, read_csv

logger = logging.getLogger(__name__)


def sanitize_fields(fieldnames):
    # return {fieldname:  re.sub('[^0-9a-zA-Z]+', '_', fieldname) for fieldname in fieldnames}
    return {fieldname: fieldname.replace(" ", "_") for fieldname in fieldnames}


def validate_fieldnames(fieldnames):
    for fieldname in fieldnames:
        if not re.match("^[a-zA-Z0-9_ -]*$", fieldname):

            raise BadCaptureSchemaError(
                'Value "{}" can only contain letters, numbers and underscores and spaces.'.format(
                    fieldname
                )
            )


def make_schema(dataframe):

    invalid_columns = []
    schema = {}
    for index, dtype in enumerate(dataframe.dtypes):
        if (
            dtype not in ["int64", "float64"]
            and dataframe.columns[index] != "timestamp"
        ):
            invalid_columns.append(dataframe.columns[index])

        column_dtype = None
        if dtype in ["int64"]:
            column_dtype = "int"
        elif dtype in ["string"]:
            column_dtype = "string"
        elif dtype in ["float64"]:
            column_dtype = "float"

        schema[dataframe.columns[index].replace(" ", "_")] = {
            "type": column_dtype,
        }

    if invalid_columns:
        raise BadCaptureSchemaError(
            "Invalid values in column(s) {}. All columns must contain only numeric data.".format(
                ",".join(invalid_columns)
            )
        )

    return schema


class FileReader(object):
    _schema = None
    _mapping = None
    _dataframe = None
    _fieldnames = None

    @property
    def schema(self):
        """Creates a schema and returns it."""
        return self._schema

    @property
    def column_mapping(self):
        return self._mapping

    @property
    def fieldnames(self):
        return self._fieldnames

    @property
    def num_samples(self):
        return len(self._dataframe)


class CSVFileReader(FileReader):
    """Allows reading of CSV Files"""

    def __init__(self, file_path):
        self._file_path = file_path

        with open(file_path, "r") as fid:
            reader = csv.DictReader(fid)

            if len(reader.fieldnames) is not len(set(reader.fieldnames)):
                raise BadCaptureSchemaError(
                    "Invalid file schema: duplicate column names are not allowed."
                )

            if any(not x for x in reader.fieldnames):
                raise BadCaptureSchemaError(
                    "Invalid column name: blank column names are not allowed."
                )

            validate_fieldnames(reader.fieldnames)

            self._mapping = sanitize_fields(reader.fieldnames)

            self._fieldnames = reader.fieldnames

        if "sequence" in self.fieldnames:
            self._dataframe = read_csv(file_path, index_col="sequence")
        else:
            self._dataframe = read_csv(file_path)
            self._dataframe.rename_axis(index="sequence", inplace=True)
            self._dataframe.to_csv(file_path)
            self._mapping["sequence"] = "sequence"

        self._schema = make_schema(self._dataframe)

        self._num_samples = len(self._dataframe)


class WaveFileReader(FileReader):
    """Allows reading of WAV Files"""

    def __init__(self, file_path):
        self._file_path = file_path

        with wave.open(file_path, "rb") as wave_reader:
            waveFrames = wave_reader.readframes(wave_reader.getnframes())
            waveData = np.fromstring(waveFrames, dtype=np.int16).reshape(
                (-1, wave_reader.getnchannels())
            )
            columns = [
                "channel_{}".format(i) for i in range(wave_reader.getnchannels())
            ]
            self._dataframe = DataFrame(waveData, columns=columns).rename_axis(
                index="sequence"
            )

            self._schema = {key: {"type": "int16"} for index, key in enumerate(columns)}

    def to_CSVFileReader(self, tmp_file_path):
        self._dataframe.to_csv(tmp_file_path, index=None)

        return CSVFileReader(tmp_file_path)
