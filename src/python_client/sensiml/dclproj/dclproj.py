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
import sqlite3
import uuid
import wave
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

from sensiml.dclproj.datasegments import DataSegment, DataSegments
from sensiml.dclproj.utils import mfcc, plot_segments_labels
from sensiml.dclproj.vizualization import plot_segments


class DCLProject:
    """
    The DCLProject class provides read-only access to the .dclproj file that is associated with a Data Capture Lab project. The
    are a number of helper functions for visualizations and queries.


    dclproj_path = '<PATH-To-File.dclproj>'

    dcl = DCLProject(path=dclproj_path)


    """

    def __init__(self, path: Optional[str] = None):
        self._path = path
        self._conn = None
        self._tables = None
        self._verbose = False

        if self._path:
            self.create_connection(self._path)

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        if isinstance(value, bool):
            self._verbose = value
        else:
            print("verbose must be either True or False.")

    @property
    def data_dir(self) -> str:

        if self._path is None:
            raise Exception("Path is not set!")

        return os.path.join(self._path, "data")

    def _set_table_list(self):
        cursorObj = self._conn.cursor()

        cursorObj.execute('SELECT name from sqlite_master where type= "table"')

        self._tables = [x[0] for x in cursorObj.fetchall()]

    def create_connection(self, db_file: str) -> None:
        """create a database connection to the SQLite database specified by db_file

        :param db_file: database file
        :return: None
        """
        self._path = os.path.dirname(db_file)
        if not os.path.exists(db_file):
            print(f"database file not found at {db_file}")
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Exception as e:
            print(e)
            raise e

        self._conn = conn
        self._set_table_list()

    def _execute_query(self, query: str, header: str = None) -> DataFrame:

        cur = self._conn.cursor()

        if self.verbose:
            print(query)

        cur.execute(query)

        if header is None:
            header = [x[0] for x in cur.description]

        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append(row)

        df = pd.DataFrame(results, columns=header)

        if "uuid" in header:
            df["uuid"] = df["uuid"].apply(
                lambda x: uuid.UUID(bytes_le=x) if x else None
            )

        if "last_modified" in header:
            df["last_modified"] = pd.to_datetime(df["last_modified"])

        if "created_at" in header:
            df["created_at"] = pd.to_datetime(df["created_at"])

        if "local_status" in header:
            local_status = {
                0: "To Add",
                1: "To Update",
                "Synced": "Synced",
                2: "To Delete",
                None: "Synced",
            }
            df["local_status"] = (
                df["local_status"].fillna("Synced").apply(lambda x: local_status[x])
            )

        return df

    def _list_table_raw(self, tablename: str, filter_deleted: bool = True) -> DataFrame:

        if tablename not in self._tables:
            print("Table is not part of the database.")
            return None

        query = f"SELECT * FROM {tablename} "

        if filter_deleted:
            query += f"WHERE ({tablename}.local_status != 2 OR {tablename}.local_status IS NULL)"

        return self._execute_query(query)

    def _list_table(
        self,
        tablename: str,
        fields: List[str],
        fk_fields: Optional[Dict] = None,
        query_filter: Optional[str] = None,
        header=None,
        filter_deleted: bool = True,
    ):

        if tablename not in self._tables:
            print("Table is not part of the database.")
            return None

        select_fields = ", ".join([f"{tablename}.{field}" for field in fields])

        if fk_fields:
            select_fields += ", " + ", ".join(
                [
                    (
                        f"{fk_table}.name"
                        if fk_table != "LabelValue"
                        else f"{fk_table}.value"
                    )
                    for fk_table in fk_fields.keys()
                ]
            )

        query_select = f"SELECT {select_fields} FROM {tablename} "

        query_join = ""

        if fk_fields:
            join_fields = []
            for fk_table, fk_field in fk_fields.items():
                join_fields.append(
                    "LEFT JOIN {fk_table} ON {fk_table}.id = {tablename}.{fk_field} ".format(
                        fk_table=fk_table, tablename=tablename, fk_field=fk_field
                    )
                )
            query_join += " ".join(join_fields)

        if query_filter and filter_deleted:
            query_where = " ".join(
                [
                    query_filter,
                    f"AND ({tablename}.local_status != 2  OR {tablename}.local_status IS NULL)",
                ]
            )
        elif filter_deleted:
            query_where = f" WHERE ({tablename}.local_status != 2  OR {tablename}.local_status IS NULL)"
        else:
            query_where = " "

        if fk_fields and not header:
            header = fields + list(fk_fields.values())

        return self._execute_query(query_select + query_join + query_where, header)

    def _list_captures_metadata(self) -> DataFrame:
        """returns a dataframe containing the capture name and the associated metadata"""

        fields = ["uuid"]

        fk_fields = OrderedDict(
            [("Capture", "capture"), ("LabelValue", "label_value"), ("Label", "label")]
        )

        df = self._list_table("CaptureMetadataValue", fields, fk_fields=fk_fields)

        M = []
        for capture_name in df.capture.unique():
            caps_dict = df[df.capture == capture_name][
                ["label", "label_value"]
            ].to_dict(orient="records")
            tmp = {"capture": capture_name}
            for item in caps_dict:
                tmp[item["label"]] = item["label_value"]
            M.append(tmp)

        return DataFrame(M).fillna("")

    def _capture_metdata_dict(self) -> dict:
        """returns a dictionary where the key is the name of the capture and the value is a dictionary of metadata_name metdata_value pairs"""
        capture_metadata = self._list_captures_metadata().to_dict(orient="rows")
        capture_metadata_dict = {}
        for item in capture_metadata:
            capture_name = item.pop("capture")
            capture_metadata_dict[capture_name] = item

        return capture_metadata_dict

    def list_captures(self, include_metadata: bool = True) -> DataFrame:
        """List the captures in the DCLI project file

        Args:
            include_metadata (bool, optional): If True return the associated metadata information with each capture. Defaults to True.

        Returns:
            DataFrame: DataFrame containing the capture information
        """

        fields = [
            "uuid",
            "name",
            "file_size",
            "number_samples",
            "set_sample_rate",
            "created_at",
            "local_status",
            "last_modified",
        ]

        fk_fields = OrderedDict([("CaptureConfiguration", "capture_configuration")])

        df = self._list_table("Capture", fields=fields, fk_fields=fk_fields)

        if not include_metadata or self._list_captures_metadata().shape[0] == 0:
            return df

        return df.merge(
            self._list_captures_metadata(),
            left_on="name",
            right_on="capture",
            how="left",
        ).drop("capture", axis=1)

    def list_sessions(self) -> DataFrame:
        fields = [
            "id",
            "name",
            "parameters",
            "custom",
            "preprocess",
            "created_at",
            "local_status",
            "last_modified",
        ]

        fk_fields = OrderedDict([])

        return self._list_table("Segmenter", fields, fk_fields)

    def list_capture_segments(
        self,
        captures: Optional[List] = None,
        sessions: Optional[List] = None,
        include_ids: bool = False,
    ) -> DataFrame:
        """Returns a DataFrame of segment information that are in the captures and sessions specified

        Args:
            captures (Optional[List], optional): A list of captures to return segments about. Defaults to None.
            sessions (Optional[List], optional): A list of sessions to return segments for. Defaults to None.

        Returns:
            DataFrame:
        """

        if captures is not None and isinstance(captures, str):
            captures = [captures]
        if sessions is not None and isinstance(sessions, str):
            sessions = [sessions]

        query_filter = ""

        def create_select(select):
            return ", ".join([f'"{x}"' for x in select])

        if captures and sessions:
            query_filter = (
                "WHERE Capture.name in ({}) ".format(create_select(captures))
                + f"AND Segmenter.name in ({create_select(sessions)}) "
            )

        elif captures:
            query_filter = f"WHERE Capture.name in ({create_select(captures)}) "
        elif sessions:
            query_filter += f"WHERE Segmenter.name in ({create_select(sessions)}) "

        fields = [
            "uuid",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "created_at",
            "last_modified",
        ]

        fk_fields = OrderedDict(
            [
                ("Segmenter", "segmenter"),
                ("Capture", "capture"),
                ("LabelValue", "label_value"),
                ("Label", "label"),
            ]
        )

        if include_ids:
            fields += ["segmenter", "capture", "label", "label_value"]
            header = [
                "uuid",
                "capture_sample_sequence_start",
                "capture_sample_sequence_end",
                "created_at",
                "last_modified",
                "segmenter_id",
                "capture_id",
                "label_id",
                "label_value_id",
                "segmenter",
                "capture",
                "label_value",
                "label",
            ]
        else:
            header = None

        return (
            self._list_table(
                "CaptureLabelValue", fields, fk_fields, query_filter, header=header
            )
            .reset_index(drop=True)
            .sort_values(by=["capture", "segmenter", "capture_sample_sequence_start"])
        )

    def get_capture_stats(self, capture: str) -> Dict:
        """Returns information about the capture

        Args:
            capture (str): name of capture

        Returns:
            Dict: information about the capture
        """
        capture_list = self.list_captures()

        if capture not in capture_list.name.values:
            raise Exception("Capture not found!")

        return capture_list[capture_list.name == capture].to_dict(orient="records")[0]

    def get_capture_metadata(
        self, capture: str = None, include_ids: bool = False
    ) -> DataFrame:
        """Gets the metadata for the specified capture

        Args:
            capture (str): name of the capture file

        Returns:
            DataFrame: DataFrame containing the metadata associated with this capture
        """

        fields = ["uuid"]

        fk_fields = OrderedDict(
            [("Capture", "capture"), ("LabelValue", "label_value"), ("Label", "label")]
        )

        if include_ids:
            fields += ["capture", "label_value", "label"]
            header = header = [
                "uuid",
                "capture_id",
                "label_value_id",
                "label_id",
                "capture",
                "label_value",
                "label",
            ]
        else:
            header = None

        df = self._list_table(
            "CaptureMetadataValue", fields, fk_fields=fk_fields, header=header
        )

        if capture is not None:
            return df[df["capture"] == capture]

        return df

    def get_segments(self, sessions: Optional[List] = None):
        """
        Returns a DataSegment object of the specified session


        Args:
            session (str):  name of session where the labels are
        """

        if sessions is not None and isinstance(sessions, str):
            sessions = [sessions]

        labels = self.list_capture_segments(captures=None, sessions=sessions)

        capture_metadata = self._capture_metdata_dict()

        data_segments = DataSegments()

        cached_df = None
        capture_index = 4
        for index, label in enumerate(
            labels[
                [
                    "capture_sample_sequence_start",
                    "capture_sample_sequence_end",
                    "uuid",
                    "label_value",
                    "capture",
                    "segmenter",
                ]
            ].values
        ):
            # TODO: read wave file if file is .wav#
            if cached_df != label[capture_index]:
                tmp_df = self.get_capture(label[capture_index])
                cached_df = label[capture_index]

            data_segments.append(
                DataSegment(
                    segment_id=index,
                    capture_sample_sequence_start=label[0],
                    capture_sample_sequence_end=label[1],
                    data=tmp_df.loc[label[0] : label[1]].values.T,
                    columns=tmp_df.columns.to_list(),
                    session=label[5],
                    label_value=label[3],
                    uuid=label[2],
                    capture=label[4],
                    extra_metadata=capture_metadata[label[4]],
                )
            )

        return data_segments

    def get_capture_segments(
        self, captures: Optional[List] = None, sessions: Optional[List] = None
    ):
        """
        Returns a DataSegment object of the specified capture and session


        Args:
            capture_name (str): name of capture
            session (str):  name of session where the labels are
        """
        if captures is not None and isinstance(captures, str):
            captures = [captures]
        if sessions is not None and isinstance(sessions, str):
            sessions = [sessions]

        labels = self.list_capture_segments(captures=captures, sessions=sessions)

        capture_metadata = self._capture_metdata_dict()

        data_segments = DataSegments()

        cached_df = None
        capture_index = 4
        for index, label in enumerate(
            labels[
                [
                    "capture_sample_sequence_start",
                    "capture_sample_sequence_end",
                    "uuid",
                    "label_value",
                    "capture",
                    "segmenter",
                ]
            ].values
        ):
            # TODO: read wave file if file is .wav#
            if cached_df != label[capture_index]:
                tmp_df = self.get_capture(label[capture_index])
                cached_df = label[capture_index]

            data_segments.append(
                DataSegment(
                    segment_id=index,
                    capture_sample_sequence_start=label[0],
                    capture_sample_sequence_end=label[1],
                    data=tmp_df.loc[label[0] : label[1]].values.T,
                    columns=tmp_df.columns.to_list(),
                    session=label[5],
                    label_value=label[3],
                    uuid=label[2],
                    capture=label[4],
                    extra_metadata=capture_metadata[label[4]],
                )
            )

        return data_segments

    def get_capture(self, capture_name: str) -> DataFrame:
        """
        Returns the capture as a DataFrame

        Args:
            capture_name (str): name of capture
        """

        # TODO: read wave file if file is .wav
        ext = capture_name.split(".")[-1]

        if not os.path.exists(os.path.join(self.data_dir, capture_name)):
            raise Exception(
                f"File {os.path.join(self.data_dir, capture_name)} does not exist!"
            )

        if ext == "csv":
            tmp_df = pd.read_csv(
                os.path.join(self.data_dir, capture_name), index_col="sequence"
            )
        elif ext == "wav":
            with wave.open(
                os.path.join(self.data_dir, capture_name), "rb"
            ) as wave_reader:
                waveFrames = wave_reader.readframes(wave_reader.getnframes())
                waveData = np.fromstring(waveFrames, dtype=np.int16).reshape(
                    (-1, wave_reader.getnchannels())
                )
                columns = [f"channel_{i}" for i in range(wave_reader.getnchannels())]
                tmp_df = DataFrame(waveData, columns=columns).rename_axis(
                    index="sequence"
                )

        return tmp_df

    def get_captures(self, capture_names: Optional[List[str]] = None) -> DataFrame:
        """
        Returns the capture as a list of dataframes

        Args:
            capture_names (List[str]): name of captures to return, if None returns all captures
        """
        if capture_names is None:
            capture_names = os.listdir(self.data_dir)

        return {
            capture_name: self.get_capture(capture_name)
            for capture_name in capture_names
        }

    def plot_segment_labels(
        self,
        capture_names: List[str],
        session: str,
        columns: Optional[List[str]] = None,
        transforms: Optional[List[Dict]] = None,
        figsize: Tuple = (30, 8),
        ylim: Optional[Tuple] = None,
        xlim: Optional[Tuple] = None,
    ) -> None:
        """
        Creates a plot of the labels and raw signal data for a session and one or more capture files.

        Args:
            capture_names (List[str]): List if captures to plot
            session (str):  name of session to pull the labels from
            columns (list): a list of columns to plot from the data
             label the value is the label it was should be renamed to
            transforms: additional fucntions to apply prior to plotting the data


        Examples:
            >>> def sum_columns(x):
            >>>     return x[['Column1', 'Column2']].sum()

            >>> func = {'name':'sum','func':sum_columns, 'type':'transform'}

            >>> dcl.plot_segment_labels(captures, session_name, columns=['sum'], transforms=[func])

            >>> # example of multiple transforms executed in order

            >>> def sum_columns(x):
            >>>     return x[['Column1', 'Column2']].sum()

            >>> def remove_offset(x):
            >>>    x['Column1']-=100
            >>>    x['Column2']-=200
            >>>    return x

            >>> func2 = {'name':'filter','func':remove_offset, "type":'filter', "columns":['Column1', 'Column2']}
            >>> func1 = {'name':'sum','func':sum_columns, "type":'transform'}

            >>> dcl.plot_segment_labels(captures, session_name, columns=['Column1', 'Column2', 'sum'], transforms=[func1, func2])
        """

        sessions = self.list_sessions()
        session_id = sessions[sessions.name == session].id.values[0]
        clv = self._list_table_raw("CaptureLabelValue")
        label_value_ids = clv[clv.segmenter == session_id].label_value.unique()
        lv = self._list_table_raw("LabelValue")
        labels = sorted(lv[lv.id.isin(label_value_ids)].value.values.tolist())
        class_map = {label: index for index, label in enumerate(labels)}

        M = []
        current_start = 0

        plt.figure(figsize=figsize)
        currentAxis = plt.gca()

        if isinstance(capture_names, str):
            capture_names = [capture_names]

        for capture_name in capture_names:

            segments = self.list_capture_segments(
                captures=[capture_name], sessions=[session]
            )

            if xlim:
                segments = segments[
                    (segments.capture_sample_sequence_start < xlim[1])
                    & (segments.capture_sample_sequence_end > xlim[0])
                ]

            capture = self.get_capture(capture_name)
            M.append(capture)

            plot_segments(
                segments,
                capture,
                capture_name=capture_name,
                labels=list(class_map.keys()),
                current_start=current_start,
                ylim=ylim,
                figsize=figsize,
                currentAxis=currentAxis,
            )

            current_start += capture.shape[0]

        capture = pd.concat(M)

        if transforms is not None:
            for func in transforms:
                if func["type"] == "transform":
                    capture[func["name"]] = capture.apply(
                        lambda x: func["func"](x), axis=func.get("axis", 1)
                    )

                if func["type"] == "filter":
                    capture[func["columns"]] = capture.apply(
                        lambda x: func["func"](x), axis=func.get("axis", 1)
                    )

        if columns is None:
            columns = capture.columns

        capture[columns].reset_index(drop=True).plot(
            figsize=figsize,
            ax=currentAxis,
            title="session: '{session}'".format(capture=capture_name, session=session),
            ylim=ylim,
            xlim=xlim,
        )

        return capture.reset_index(drop=True)

    def plot_frequency(
        self,
        capture_name: str,
        channel: str,
        sample_freq: int = 16000,
        figsize: Tuple = (30, 4),
        session: Optional[str] = None,
    ):

        nrows = 3
        data = self.get_capture(capture_name)

        fig, axes = plt.subplots(
            nrows=nrows, ncols=1, figsize=(figsize[0], figsize[1] * nrows)
        )
        fig.tight_layout()

        data.plot(ax=axes[0], title=capture_name, xlim=(0, data.shape[0]), xlabel="")

        _ = axes[1].specgram(data[channel], NFFT=512)
        axes[1].set_title("Sepctrogram")

        axes[2].imshow(
            mfcc(data, channel, sample_freq=sample_freq, plot_all=False), aspect="auto"
        )
        axes[2].set_title("MFCC")

        if session:
            segments = self.list_capture_segments(
                captures=[capture_name], sessions=[session]
            )

            plot_segments_labels(
                segments,
                axes=axes[0],
                y_label=(
                    data[channel].min(),
                    int(data[channel].max()) - int(data[channel].min()),
                ),
            )

        plt.subplots_adjust(hspace=0.2)

        return axes
