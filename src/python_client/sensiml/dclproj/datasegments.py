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
import json
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame, concat

from sensiml.dclproj.confusion_matrix import ConfusionMatrix
from sensiml.dclproj.utils import upload_datasegments
from sensiml.dclproj.vizualization import plot_segments


class DataSegment(object):
    def __init__(
        self,
        segment_id: int,
        capture_sample_sequence_start: int,
        capture_sample_sequence_end: int,
        columns: Optional[list] = None,
        data: Optional[np.array] = None,
        session: Optional[str] = None,
        label_value: Optional[str] = None,
        uuid: Optional[str] = None,
        capture: Optional[str] = None,
        extra_metadata: Optional[dict] = None,
        **kwargs,
    ):
        self._metadata = [
            "label_value",
            "capture",
            "segment_id",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
            "session",
            "uuid",
            "segment_length",
        ]
        self._label_value = "" if None else str(label_value)
        self._session = session
        self._segment_id = segment_id
        self._uuid = uuid
        self._capture = capture
        self._data = data
        self._columns = columns
        self._capture_sample_sequence_start = capture_sample_sequence_start
        self._capture_sample_sequence_end = capture_sample_sequence_end
        self._extra_metadata = extra_metadata

    def __repr__(self):
        return str(self.metadata)

    def copy(self):
        """Returns a deepcopy of this item

        Returns:
            DataSegment: Returns a deepcopy of the current DataSegment object
        """
        return copy.deepcopy(self)

    def to_dict(self):
        tmp = self.metadata
        tmp["columns"] = self.columns
        tmp["data"] = self.data

        return tmp

    @property
    def metadata(self):
        tmp_metadata = {k: getattr(self, f"_{k}") for k in self._metadata}
        if self._extra_metadata:
            tmp_metadata.update(self._extra_metadata)

        return tmp_metadata

    @property
    def capture(self):
        return self._capture

    @property
    def segment_id(self):
        return self._segment_id

    @property
    def label_value(self):
        return self._label_value

    @property
    def uuid(self):
        return str(self._uuid)

    @property
    def has_data(self):
        if self._data is not None:
            return True

        return False

    @property
    def data(self):
        return self._data

    @property
    def segment_length(self):
        return self._capture_sample_sequence_end - self._capture_sample_sequence_start

    @property
    def _segment_length(self):
        return self.segment_length

    @property
    def columns(self):
        return self._columns

    @property
    def capture_sample_sequence_start(self):
        return self._capture_sample_sequence_start

    @property
    def capture_sample_sequence_end(self):
        return self._capture_sample_sequence_end

    @property
    def start(self):
        return self.capture_sample_sequence_start

    @property
    def end(self):
        return self.capture_sample_sequence_end

    @start.setter
    def start(self, value):
        self.capture_sample_sequence_start = value

    @end.setter
    def end(self, value):
        self.capture_sample_sequence_end = value

    @label_value.setter
    def label_value(self, value):
        if value is None:
            self._label_value = "Unknown"
        else:
            self._label_value = value

    @property
    def session(self):
        return self._session

    def to_dataframe(self):
        if self.data is None:
            return

        return DataFrame(self.data.T, columns=self.columns)

    def get_column_index(self, column):
        if self._columns is None:
            return

        return self._columns.index(column)

    def plot(self, figsize: Tuple = (30, 4), currentAxis=None, **kwargs):
        if self._data is None:
            return

        if currentAxis is None:
            plt.figure(figsize=figsize)
            currentAxis = plt.gca()

        for index, axis in enumerate(self.data):
            currentAxis.plot(axis, label=self.columns[index])

        currentAxis.set_xlim(0, self.data.shape[1])

        plt.legend(loc=0)

        return currentAxis

    def plot_spectrogram(
        self, channel: str, fft_length: int = 512, figsize: Tuple = (30, 4), **kwargs
    ):
        """Plots the spectrogram for the signal.

        Args:
            channel (str): the channel/column of sensor data to use
            fft_length (int, optional): The size of the FTT length to use when computing the spectrogram. Defaults to 512.
            figsize (Tuple, optional): the size of the figure that will be created. Defaults to (30, 4).
        """
        if self._data is None:
            return

        fig, axis = plt.subplots(figsize=figsize)

        data = axis.specgram(
            self.data[self.get_column_index(channel)], NFFT=fft_length, **kwargs
        )


class DataSegments(object):
    def __init__(self, data: Optional[list] = None):
        self._data = []

        if data:
            self._data = data

    @property
    def data(self):
        return self._data

    def __repr__(self):
        display(self.to_dataframe())
        return ""

    def __str__(self):
        return self.to_dataframe().__str__()

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __add__(self, value):
        return DataSegments(self._data + value._data)

    def __getitem__(self, key):
        return self._data[key]

    def head(self, value=5):
        return self.to_dataframe().head(value)

    def append(self, data_segment: DataSegment):
        """Append a DataSegment to the current DataSegments List

        Args:
            data_segment (DataSegment):
        """
        self._data.append(data_segment)

    def extend(self, data_segments: DataSegment):
        """Extend the current DataSegments object with another DataSegments object

        Args:
            data_segments (DataSegment):
        """

        self._data.extend(data_segments._data)

    @property
    def only_metadata(self):
        if self._data is None:
            return True

        if self._data[0].data is None:
            return True

        return False

    def filter_by_metadata(self, filter: dict, exclude: bool = False):
        """
        Applies a filter to the datasegments and returns a filtered version


        Args:
            filter (dict): dictionary of of lists, where the key is the metadata name to filter and the values are a list of metadata values to filter by
            exclude (bool): the filter is exclusive if True, otherwise the filter is inclusive
        """
        filtered_ds = DataSegments()

        for segment in self._data:
            for filter_key, filter_values in filter.items():
                if exclude:
                    if segment.metadata.get(filter_key) not in filter_values:
                        filtered_ds.append(segment)
                        break
                elif segment.metadata.get(filter_key) in filter_values:
                    filtered_ds.append(segment)
                    break

        return filtered_ds

    def to_dataframe(self, metadata_only: bool = True):
        M = []

        if not self._data:
            return None

        if self.only_metadata:
            for segment in self._data:
                M.append(segment.metadata)

            return DataFrame(M)

        for segment in self.data:
            if metadata_only:
                M.append(DataFrame([segment.metadata]))
            else:
                tmp_df = DataFrame(segment.data.T, columns=segment.columns)
                M.append(tmp_df.assign(**segment.metadata))

        return concat(M).reset_index(drop=True)

    def to_timeseries(self):
        """Converts the datasegments into a timeseries object used by tsfresh"""
        M = []
        Y = []

        if not self._data:
            return None

        for segment in self.data:
            tmp_df = DataFrame(segment.data.T, columns=segment.columns)
            tmp_df["time"] = tmp_df.index
            tmp_df["id"] = segment.segment_id
            M.append(tmp_df)
            Y.append(segment.metadata)
            Y[-1]["id"] = segment.segment_id

        return concat(M).reset_index(drop=True), DataFrame(Y)

    def apply(self, func, **kwargs) -> DataFrame:
        """Apply a function to all the segments in the DataSegments object and return a DataFrame of the resulting generated features for each datasegment.

        Args:
            func (_type_): and function object which takes a DataSegment as its first input and kwargs as the following

        Returns:
            DataFrame: A DataFrame of the generated features from the applied function
        """

        feature_vectors = []
        for segment in self.data:
            tmp_df = func(segment, **kwargs)
            feature_vectors.append(tmp_df.assign(**segment["metadata"]))

        return concat(feature_vectors).reset_index(drop=True)

    def iter_dataframe(self):
        if self.only_metadata:
            for segment in self._data:
                yield DataFrame([segment["metadata"]])
        else:
            for segment in self._data:
                tmp_df = DataFrame(segment["data"].T, columns=segment["columns"])

                yield tmp_df.assign(**segment["metadata"])

    def iterrows(self):
        for index, data_segment in enumerate(self.data):
            yield (index, data_segment.to_dict())

    def to_dcli(
        self,
        filename: Optional[str] = None,
        session: Optional[str] = None,
        verification_id: Optional[str] = None,
        session_parameters: Optional[dict] = None,
    ) -> List:
        """Creates a .dcli file describing the segment information that can be imported into the Data Capture Lab

        Args:
            filename (Optional[str], optional): The name of the file to save it to, if None no file is created.. Defaults to None.
            session (Optional[str], optional): The name of a session to use when creating the DCLI file. if None the session from the DataSegment objects are used.. Defaults to None.

        Returns:
            List: DCLI formatted segments
        """

        def get_capture_index(dcli_capture, file_name):
            for index, capture in enumerate(dcli_capture):
                if file_name == capture["file_name"]:
                    return index

            return None

        def get_session_index(sessions, session_name):
            for index, session in enumerate(sessions):
                if session_name == session["session_name"]:
                    return index

            return None

        dcli_capture = []

        for segment in self._data:
            capture_index = get_capture_index(dcli_capture, segment.capture)

            if capture_index is None:
                dcli_capture.append({"file_name": segment.capture, "sessions": []})
                capture_index = -1

            session_index = get_session_index(
                dcli_capture[capture_index]["sessions"],
                segment.session if session is None else session,
            )

            if session_index is None:
                if session is None:
                    dcli_capture[capture_index]["sessions"].extend(
                        [{"session_name": segment.session, "segments": []}]
                    )
                else:
                    dcli_capture[capture_index]["sessions"].extend(
                        [{"session_name": session, "segments": []}]
                    )

                if verification_id:
                    dcli_capture[capture_index]["sessions"][-1][
                        "verification_id"
                    ] = verification_id
                if session_parameters:
                    dcli_capture[capture_index]["sessions"][-1][
                        "session_parameters"
                    ] = session_parameters

                session_index = -1

            dcli_capture[capture_index]["sessions"][session_index]["segments"].append(
                {
                    "name": "Label",
                    "value": segment.label_value,
                    "start": segment.start,
                    "end": segment.end,
                }
            )

        if filename is not None:
            print("writing dcli file to", filename)
            json.dump(dcli_capture, open(filename, "w"))

        return dcli_capture

    def to_audacity(self, rate: int = 16000) -> List:
        """Creates multiple files with the naming convention file_{capture_name}session{session_name}.txt.

        These can be imported into Audacity directly going to File->Import->Labels

        Args:
            rate (int): Audacity uses the actual time and note number of samples. Set the rate to the sample rate for the captured date. Default is 16000.
        """

        dcli = self.to_dcli()

        for capture in dcli:
            for session in capture["sessions"]:
                outfile = "file_{capture}_session_{session}.txt".format(
                    capture=capture["file_name"], session=session["session_name"]
                )
                with open(
                    outfile,
                    "w",
                ) as out:
                    for segment in session["segments"]:
                        out.write(
                            "{start_time}\t{end_time}\t{label}\n".format(
                                start_time=segment["start"] / rate,
                                end_time=segment["end"] / rate,
                                label=segment["value"],
                            )
                        )
                    print(f"labels written to {outfile}")

    @property
    def label_values(self) -> List:
        """List all the labels in the DataSegments object"""

        label_values = set()
        for segment in self._data:
            label_values.add(segment.label_value)

        return sorted(list(label_values))

    def merge_label_values(self, data_segments: dict) -> List:
        """Merges label values between to data segments.

        Args:
            data_segments (dict): The datasegment object to merge label values with

        Returns:
            List: The sorted union of the label values from both datasegments
        """

        return sorted(
            list(set(data_segments.label_values).union(set(self.label_values)))
        )

    def merge_segments(self, delta: int = 1, verbose=False):
        """Merge segments that overlap or are within delta of each other.

        Args:
            delta (int, optional): The distance between two nonoverlapping segments where they will still be merged. Defaults to 1.

        Returns:
            DataFrame: A DataFrame consisting of the merged segments
        """

        return merge_segments(self, delta=delta, verbose=verbose)

    def filter_segments(self, min_length: int = 10000):
        """Merges data segments that are within a distance delta of each other and have the same class name."""

        new_datasegments = DataSegments()

        for _, segment in enumerate(self.data):
            if segment.segment_length > min_length:
                new_datasegments.append(segment)

        print(
            "Original Segments:",
            len(self),
            "Filtered Segments:",
            len(new_datasegments),
        )

        return new_datasegments

    def remove_overlap(self, verbose: bool = False, inplace: bool = False):
        """Removes the overlap between segments by setting the segment start and
        end of overlapping segments to the same point, halfway between the overlapping edges.

        Args:
            dcl (DCLProject): A DCLProject object that is connected to the DCLI file

        Returns:
            DataSegments: A DataSegments object consisting of the merged segments
        """
        return remove_overlap(self, verbose=verbose, inplace=inplace)

    def join_segments(self, delta: Optional[int] = None, inplace: bool = False):
        """Joins adjacent segments so that there is no empty space between segments.

        Args:
            dcl (DCLProject): A DCLProject object that is connected to the DCLI file
            delta (int): Segments outside this range will not be joined. If None, all neighboring segments will be merged regardless of the distance. Default is None.

        Returns:
            DataSegments: A DataSegments object consisting of the merged segments
        """

        return join_segments(self, delta=delta, inplace=inplace)

    def plot_segments(
        self,
        capture: Optional[DataFrame] = None,
        capture_name: Optional[str] = None,
        labels: Optional[list] = None,
        **kwargs,
    ):
        """plot the datasegment labels

        Args:
            capture (DataFrame, optional): DataFrame of capture data. Defaults to None.
            capture_name (str, optional): name of the capture. Defaults to None.
            labels (List[str], optional): List of labels to use. Defaults to None.
            kwargs
        """

        plot_segments(
            self, capture=capture, capture_name=capture_name, labels=labels, **kwargs
        )

    def nearest_labels(
        self,
        ground_truth_segments,
        overlap_pct: float = 0.5,
        verbose=False,
        keep_default=False,
    ) -> dict:
        """Computes the nearest labels in the current DataSegment to a ground truth DataSegments and updates the labels with
        the ground truth label.

        Args:
            pred_segments (list): list of segments from prediction file
            ground_truth_segments (list): list of segments from manually labeled file

        Returns:
            DataSegment: A DataSegments object with the new updated labels
        """
        tmp_segments = copy.deepcopy(self)
        # Loop over all predicted segments
        for new_seg in tmp_segments:
            # Loop over real segments to find all real segments that the predicted segment overlaps with
            # (discard predictions that overlap w/ nothing)
            last_overlap = 0
            for gt_seg in ground_truth_segments:
                if gt_seg.segment_length == 0:
                    break
                # If the next real segment begins after the predicted one ends then there will be no more overlapping segments
                if gt_seg.start > new_seg.end:
                    break
                # If the next real segment ends before the predicted one starts then it won't overlap so we should skip it
                if gt_seg.end < new_seg.start:
                    continue
                overlap = _calculate_overlap_percent(gt_seg, new_seg)
                # Keep track of what the prediction was and how it compared to the actual label IF it is over the overlap threshold
                if overlap >= overlap_pct:
                    if overlap > last_overlap:
                        if verbose and new_seg.label_value != gt_seg.label_value:
                            print(
                                f"Updating {new_seg.segment_id} from {new_seg.label_value} to {gt_seg.label_value}"
                            )
                        new_seg.label_value = gt_seg.label_value
                        last_overlap = overlap

            if last_overlap == 0:
                if verbose and not keep_default:
                    print(
                        f"No matching label found for {new_seg.segment_id} setting to None"
                    )
                if not keep_default:
                    new_seg.label_value = None

        return tmp_segments

    def confusion_matrix(
        self, ground_truth: dict, overlap_pct: float = 0.5
    ) -> ConfusionMatrix:
        """Generate confusion matrix with this segments and overlapping segments

        Args:
            ground_truth (DataSegments): DataSegments to use as the ground truth
            overlap_pct (float, optional): amount of overlap to consider the segments overlapping. Defaults to 0.5.

        Returns:
            ConfusionMatrix: confusion matrix object
        """
        return ConfusionMatrix(self, ground_truth, overlap_percent=overlap_pct)

    def upload(self, client, default_label: str, verbose: bool = True):
        """Upload the segments

        Args:
            client (client): Client logged in and connected to the target project
            default_label (str): default label to use
            verbose (bool, optional): prints out info. Defaults to True.
        """

        upload_datasegments(client, self, default_label=default_label, verbose=verbose)


def _get_percent(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 2) if denominator and numerator else 0


def _calculate_overlap_percent(s1, s2) -> float:
    # calculate overlap between labels
    label_overlap = min(s1.end, s2.end) - max(s1.start, s2.start)
    # calculate length of label 2
    range_of_label_2 = s2.end - s2.start
    # return overlap percent
    return _get_percent(label_overlap, range_of_label_2)


def check_overlap(s1, s2):
    return (
        True
        if max(
            0,
            min(s1.end, s2.end) - max(s1.start, s2.start),
        )
        > 0
        else False
    )


def check_near(s1, s2, delta):
    if delta is None:
        return True

    return True if abs(s2.start - s1.end) < delta else False


def merge_segments(
    segments: DataSegments, delta: int = 10, verbose=False
) -> DataSegments:
    """Merges data segments that are within a distance delta of each other and have the same class name.

    Args:
        segments (DataFrame): A DataFrame of segments
        delta (int, optional): The distance between two nonoverlapping segments where they will still be merged. Defaults to 10.

    Returns:
        DataFrame: DataFrame containing the merged segments
    """

    seg_groups = segments.to_dataframe().groupby(["session", "capture"])

    new_segments = DataSegments()
    for key in seg_groups.groups.keys():
        if verbose:
            print("Group", key)

        segment_list = (
            seg_groups.get_group(key)
            .sort_values(by="capture_sample_sequence_start")
            .index.values.tolist()
        )
        merge_list = []

        for index, segment_index in enumerate(segment_list):
            segment = segments[segment_index]
            next_segment = None

            if len(segment_list) - 1 != index:
                next_segment = segments[segment_list[index + 1]]

            if not merge_list:
                if len(segment_list) - 1 == index:
                    new_segments.append(segment)
                    continue
                elif next_segment.label_value != segment.label_value:
                    new_segments.append(segment)
                    continue
                elif not check_near(segment, next_segment, delta) and not check_overlap(
                    segment, next_segment
                ):
                    new_segments.append(segment)
                    continue

            if (
                len(segment_list) - 1 != index
                and next_segment.label_value == segment.label_value
                and (
                    check_near(segment, next_segment, delta)
                    or check_overlap(segment, next_segment)
                )
            ):
                if not merge_list:
                    merge_list.append(index)
                merge_list.append(index + 1)

            else:
                # do merge
                if merge_list:
                    if verbose:
                        print("merging", merge_list)

                    new_segments.append(merge_segment(segments, merge_list))
                else:
                    new_segments.append(segment)

                merge_list = []

        if merge_list:
            if verbose:
                print("merging", merge_list)
            new_segments.append(merge_segment(segments, merge_list))

    print("Original Segments:", len(segments), "Merged Segments:", len(new_segments))

    return new_segments


def merge_segment(segments, merge_list):
    tmp_segment = segments[merge_list[0]].copy()

    end = tmp_segment.end

    for segment_index in merge_list:
        if end < segments[segment_index].end:
            end = segments[segment_index].end

    tmp_segment._capture_sample_sequence_end = end

    if tmp_segment.has_data:
        capature_start = tmp_segment.start
        data = np.zeros((tmp_segment.data.shape[0], end - tmp_segment.start))
        head_index = 0
        capture_head_index = capature_start
        for segment in [segments[x] for x in merge_list]:
            segment.start + head_index
            data[:, head_index : segment.end - capature_start] = segment.data[
                :, capture_head_index - segment.start : segment.end - segment.start
            ]
            head_index += segment.end - capature_start
            capture_head_index += head_index

        tmp_segment._data = data

    return tmp_segment


def remove_overlap(
    segments: DataSegments, verbose: bool = False, inplace: bool = False
) -> DataSegments:
    """Removes the overlap between segments by setting the segment start and end of
    overlapping segments to the same point, halfway between the overlapping edges."""

    if inplace:
        new_segments = segments
    else:
        new_segments = copy.deepcopy(segments)

    seg_groups = new_segments.to_dataframe().groupby(["session", "capture"])

    for key in seg_groups.groups.keys():
        if verbose:
            print("Group", key)

        segment_list = (
            seg_groups.get_group(key)
            .sort_values(by="capture_sample_sequence_start")
            .index.values.tolist()
        )

        for index, segment_index in enumerate(segment_list[:-1]):
            segment = new_segments[segment_index]
            next_segment = new_segments[segment_list[index + 1]]

            if check_overlap(segment, next_segment):
                difference = (abs((next_segment.start - segment.end)) + 1) // 2
                segment._capture_sample_sequence_end -= difference
                next_segment._capture_sample_sequence_start += difference

                if segment.has_data:
                    segment._data = segment._data[:, :-difference]
                if next_segment.has_data:
                    next_segment._data = segment._data[:, difference:]

    return new_segments


def join_segments(
    segments, delta: Optional[int] = None, inplace: bool = False
) -> DataFrame:
    """If there are any gaps between two segments, this will bring them together so there are no unlabeled regions of data."""

    print(
        "This will drop the data, use the .refresh_data API to repopulate the data table"
    )

    if inplace:
        new_segments = segments
    else:
        new_segments = copy.deepcopy(segments)

    seg_groups = new_segments.to_dataframe().groupby(["session", "capture"])

    for key in seg_groups.groups.keys():
        segment_list = (
            seg_groups.get_group(key)
            .sort_values(by="capture_sample_sequence_start")
            .index.values.tolist()
        )

        for index, segment_index in enumerate(segment_list[:-1]):
            segment = new_segments[segment_index]
            next_segment = new_segments[segment_list[index + 1]]

            if (
                not check_overlap(segment, next_segment) and True
                if delta is None
                else check_near(segment, next_segment, delta=delta)
            ):
                difference = (abs((next_segment.start - segment.end)) + 1) // 2
                segment._capture_sample_sequence_end += difference
                next_segment._capture_sample_sequence_start -= difference

        segment._data = None
        next_segment._data = None

    return new_segments
