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

from datamanager.datasegments import template_datasegment


def process_segment_results(
    input_data, seg_beg_end_list, group_columns, return_segment_index=False
):
    datasegments = []
    segment_tmp = {}
    segment_tmp["columns"] = [
        column for column in input_data.columns if column not in group_columns
    ]
    segment_tmp["metadata"] = {}

    if not seg_beg_end_list:
        return []

    for i in range(len(seg_beg_end_list)):
        tmp_seg = template_datasegment(segment_tmp)
        metadata_values = (
            input_data[group_columns]
            .iloc[seg_beg_end_list[i][0] : seg_beg_end_list[i][0] + 1]
            .values[0]
        )

        tmp_seg["metadata"].update(
            {k[0]: k[1] for k in zip(group_columns, metadata_values)}
        )
        tmp_seg["metadata"]["SegmentID"] = i
        if return_segment_index:
            tmp_seg["metadata"]["Seg_Begin"] = seg_beg_end_list[i][0]
            tmp_seg["metadata"]["Seg_End"] = seg_beg_end_list[i][1]
        else:
            tmp_seg["data"] = (
                input_data[segment_tmp["columns"]]
                .iloc[seg_beg_end_list[i][0] : seg_beg_end_list[i][1] + 1]
                .values.T
            )

        datasegments.append(tmp_seg)

    return datasegments
