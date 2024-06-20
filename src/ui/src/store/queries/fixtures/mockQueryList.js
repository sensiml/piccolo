/*
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
*/

export default {
  data: [
    {
      uuid: "a17769d6-dd38-445b-a5f8-e183ae22960f",
      name: "CDK_ALL_TYPES",
      columns: [
        "GyroscopeX",
        "GyroscopeY",
        "GyroscopeZ",
        "AccelerometerX",
        "AccelerometerY",
        "AccelerometerZ",
      ],
      label_column: "Punch",
      metadata_columns: ["segment_uuid", "Type", "Subject"],
      metadata_filter:
        "[Subject] IN [UserCDK] AND [Type] IN [Train] AND [Punch] IN [Unknown,Uppercut,Overhand,Jab,Hook,Cross]",
      segmenter_id: 1,
      combine_labels: null,
      created_at: "2020-09-12T23:46:48.9057",
      capture_configurations: [],
      last_modified: "2020-09-13T20:43:33.390853Z",
      segmenter: 1,
    },
    {
      uuid: "11271bd6-c09f-429a-beb8-2f17b671c64e",
      name: "CDK_Data",
      columns: [
        "GyroscopeX",
        "GyroscopeY",
        "GyroscopeZ",
        "AccelerometerX",
        "AccelerometerY",
        "AccelerometerZ",
      ],
      label_column: "Punch",
      metadata_columns: ["segment_uuid", "Subject", "Type"],
      metadata_filter:
        "[Subject] IN [UserCDK] AND [Type] IN [Train] AND [Punch] IN [Uppercut,Overhand,Jab,Hook,Cross]",
      segmenter_id: 2,
      combine_labels: null,
      created_at: "2020-07-17T18:59:25.0435",
      capture_configurations: [],
      last_modified: "2020-09-11T23:49:46.973336Z",
      segmenter: 2,
    },
  ],
  isFetching: false,
};
