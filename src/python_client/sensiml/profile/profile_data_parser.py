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

import json, yaml
import serial
from decimal import Decimal
from functools import reduce


class ProfileParser(object):
    def __init__(self, json_path, port, num_msgs=100, baud=115200, debug=False):
        self._port = port
        self.baud = baud
        self._is_running = False
        self._feature_times = list()
        self._feature_average_time = list()
        self._feature_cycles = list()
        self._feature_average_cycles = list()
        self._classifier_times = list()
        self._classifier_average_time = list()
        self._classifier_cycles = list()
        self._classifier_average_cycles = list()
        self._is_running = False
        self._combined_metrics = dict()
        self._max_msgs = num_msgs
        self._debug = debug

        if json_path:
            with open(json_path, "r") as f:
                self._model_desc = json.load(f)

            for model_index, model_name in self._model_desc["ModelIndexes"].items():
                mi = int(model_index)
                model_type = self._model_desc["ModelDescriptions"][mi]["ModelType"]
                self._feature_times.insert(mi, dict())
                self._feature_average_time.insert(mi, dict())
                self._feature_cycles.insert(mi, dict())
                self._feature_average_cycles.insert(mi, dict())
                self._classifier_times.insert(mi, dict())
                self._classifier_average_time.insert(mi, dict())
                self._classifier_cycles.insert(mi, dict())
                self._classifier_average_cycles.insert(mi, dict())
                for feature in self._model_desc["ModelDescriptions"][mi][
                    "FeatureFunctions"
                ]:
                    self._feature_times[mi][feature] = list()
                    self._feature_average_time[mi][feature] = 0
                    self._feature_cycles[mi][feature] = list()
                    self._feature_average_cycles[mi][feature] = 0
                self._classifier_times[mi][model_type] = list()
                self._classifier_average_time[mi][model_type] = 0
                self._classifier_cycles[mi][model_type] = list()
                self._classifier_average_cycles[mi][model_type] = 0

        else:
            self._model_desc = None

    def run(self):
        msgs_rx = 0
        self._is_running = True
        self._ser = serial.Serial(port=self._port, baudrate=self.baud)
        while msgs_rx < self._max_msgs:
            try:
                line = self._ser.readline()
                decoded = json.loads(line)
                self._parse_message(decoded)
                msgs_rx += 1
            except Exception as e:
                if self._debug:
                    print(e)
                    print(line)
                continue
        self._ser.close()
        self._combined_metrics.update(
            {
                "FeatureTimePerInference": self.feature_average_time,
                "FeatureCyclesPerInference": self.feature_average_cycles,
                "ClassifierAverageTime": self.classifier_average_time,
                "ClassifierAverageCycles": self.classifier_average_cycles,
                "RunCount": msgs_rx,
            }
        )
        print("Reader closed")

    def stop(self):
        self._is_running = False

    @property
    def combined_metrics(self):
        return self._combined_metrics

    @property
    def is_running(self):
        return self._is_running

    @property
    def feature_times(self):
        return self._feature_times

    @property
    def feature_average_time(self):
        return self._feature_average_time

    @property
    def classifier_times(self):
        return self._classifier_times

    @property
    def classifier_average_time(self):
        return self._classifier_average_time

    @property
    def feature_cycles(self):
        return self._feature_cycles

    @property
    def feature_average_cycles(self):
        return self._feature_average_cycles

    @property
    def classifier_cycles(self):
        return self._classifier_cycles

    @property
    def classifier_average_cycles(self):
        return self._classifier_average_cycles

    def _average(self, lst):
        return reduce(lambda a, b: a + b, lst) / len(lst)

    def _format_result(self, result):
        int(result)
        microseconds = (result * 1000000) % 1000000
        nanoseconds = (result * 1000000000) % 1000000000
        output = Decimal((microseconds / 1000000) + nanoseconds / 1000000000)
        output = output.quantize(Decimal("0.0000000001"))
        return output

    def _parse_message(self, data):
        model_number = data.get("ModelNumber", 0)
        string_type = data.get("Type", None)
        model_type = self._model_desc["ModelDescriptions"][model_number]["ModelType"]
        feature_index = 0
        if string_type == "Cycles":
            for k in self._feature_times[model_number].keys():
                cycles_per_sample = data["FeatureCycles"][feature_index]
                self._feature_cycles[model_number][k].append(cycles_per_sample)
                self._feature_average_cycles[model_number][k] = round(
                    self._average(self._feature_cycles[model_number][k])
                )
                self._classifier_cycles[int(model_number)][model_type].append(
                    data["ClassifierCycles"]
                )
                feature_index += 1
            self._classifier_average_cycles[int(model_number)][model_type] = round(
                self._average(self._classifier_cycles[model_number][model_type])
            )
        elif string_type == "Times":
            for k in self._feature_times[model_number].keys():
                time_per_sample = data["FeatureTimes"][feature_index]
                self._feature_times[model_number][k].append(time_per_sample)
                self._feature_average_time[model_number][k] = "{0:0.9f}".format(
                    self._format_result(
                        self._average(self._feature_times[model_number][k])
                    )
                )
                self._classifier_times[int(model_number)][model_type].append(
                    data["ClassifierTime"]
                )

                feature_index += 1
            self._classifier_average_time[int(model_number)][model_type] = (
                "{0:0.9f}".format(
                    self._format_result(
                        self._average(self._classifier_times[model_number][model_type])
                    )
                )
            )

    def to_json(self):
        return json.dumps(self._combined_metrics)

    def to_yaml(self):
        return yaml.dump(self._combined_metrics)
