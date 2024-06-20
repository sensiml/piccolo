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

import json
import logging
import os
import shutil

import pytest
from datamanager.models import KnowledgePack, Project, Sandbox, Team, TeamMember
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


@pytest.fixture
def project():
    project = Project.objects.create(
        name="APITestProject",
        team=Team.objects.get(name=TEAM_NAME),
    )
    return project


@pytest.fixture
def sandbox(project):
    sandbox = Sandbox.objects.create(
        name="TestPipeline",
        project=project,
    )
    team_members = TeamMember.objects.filter(team=project.team)
    for team_member in team_members:
        sandbox.users.add(team_member)
    return sandbox


@pytest.fixture
def knowledgepacks(project, sandbox):
    knowledgepacks = []
    for i in range(10):
        knowledgepacks.append(
            KnowledgePack.objects.create(
                name="TestKnowledgePack_{}".format(i),
                project=sandbox.project,
                neuron_array={
                    "tflite": 1000,
                    "tflite_full": 2000,
                    "tflite_quant": 3000,
                    "model_store": 4000,
                    "model_parameters": True,
                },
                sandbox=sandbox,
                model_results={
                    "model_size": 5488,
                    "metrics": {"validation": {"accuracy": 99.99}},
                },
                device_configuration={"classifier": "PME"},
                feature_summary=[
                    {"Feature": "gen_0013_GyroscopeXZeroCrossingRate"},
                    {"Feature": "gen_0014_GyroscopeYZeroCrossingRate"},
                    {"Feature": "gen_0016_AccelerometerXZeroCrossingRate"},
                ],
                cost_summary={
                    "sensors": {
                        "sram": 896,
                        "flash": 0,
                        "stack": 0,
                        "latency": 232562,
                        "cycle_count": 0,
                        "number_of_sensors": 7,
                        "max_segment_length": 61.0,
                    },
                    "pipeline": [
                        {
                            "name": "Magnitude",
                            "sram": 0,
                            "type": "transform",
                            "flash": 96,
                            "stack": 112,
                            "latency": 1098.0,
                            "cycle_count": 0.0,
                        },
                        {
                            "name": "generator_set",
                            "sram": 6.0,
                            "type": "generatorset",
                            "flash": 17235.999999999996,
                            "stack": 604,
                            "latency": 378115.12034647,
                            "cycle_count": 478240.0,
                            "per_generator_costs": {
                                "MFCC": {
                                    "name": "MFCC",
                                    "sram": 2.0,
                                    "type": "generator",
                                    "flash": 9452.0,
                                    "stack": 604,
                                    "latency": 2503.44,
                                    "cycle_count": 168238.0,
                                    "num_features": 137,
                                    "num_iterations": 6,
                                },
                                "Mean": {
                                    "name": "Mean",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 380.0,
                                    "stack": 232,
                                    "latency": 0.569194416,
                                    "cycle_count": 37088.0,
                                    "num_features": 3,
                                    "num_iterations": 3,
                                },
                                "Median": {
                                    "name": "Median",
                                    "sram": 0.8,
                                    "type": "generator",
                                    "flash": 400.0,
                                    "stack": 324,
                                    "latency": 3.2291279640000004,
                                    "cycle_count": 4087.0,
                                    "num_features": 3,
                                    "num_iterations": 3,
                                },
                                "Maximum": {
                                    "name": "Maximum",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 198,
                                    "stack": 172,
                                    "latency": 976.0,
                                    "cycle_count": 4880.0,
                                    "num_features": 1,
                                    "num_iterations": 1,
                                },
                                "Minimum": {
                                    "name": "Minimum",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 198,
                                    "stack": 172,
                                    "latency": 5856.0,
                                    "cycle_count": 4636.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Kurtosis": {
                                    "name": "Kurtosis",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 682.0,
                                    "stack": 400,
                                    "latency": 150023.4,
                                    "cycle_count": 7747.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Skewness": {
                                    "name": "Skewness",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 702.0,
                                    "stack": 400,
                                    "latency": 150169.8,
                                    "cycle_count": 8967.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Variance": {
                                    "name": "Variance",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 290,
                                    "stack": 202,
                                    "latency": 8052.0,
                                    "cycle_count": 20130.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Min Column": {
                                    "name": "Min Column",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 1,
                                    "num_iterations": 1,
                                },
                                "Absolute Sum": {
                                    "name": "Absolute Sum",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 186,
                                    "stack": 160,
                                    "latency": 653.9200000000001,
                                    "cycle_count": 37027.0,
                                    "num_features": 1,
                                    "num_iterations": 1,
                                },
                                "Absolute Area": {
                                    "name": "Absolute Area",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 273.6,
                                    "stack": 292,
                                    "latency": 1281.0,
                                    "cycle_count": 3294.0,
                                    "num_features": 1,
                                    "num_iterations": 1,
                                },
                                "Absolute Mean": {
                                    "name": "Absolute Mean",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 200,
                                    "stack": 160,
                                    "latency": 0.9486573599999999,
                                    "cycle_count": 37698.0,
                                    "num_features": 5,
                                    "num_iterations": 5,
                                },
                                "Power Spectrum": {
                                    "name": "Power Spectrum",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 90,
                                    "num_iterations": 6,
                                },
                                "Zero Crossings": {
                                    "name": "Zero Crossings",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 2,
                                    "num_iterations": 2,
                                },
                                "25th Percentile": {
                                    "name": "25th Percentile",
                                    "sram": 0.8,
                                    "type": "generator",
                                    "flash": 214.0,
                                    "stack": 256,
                                    "latency": 6.46683387,
                                    "cycle_count": 7869.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "75th Percentile": {
                                    "name": "75th Percentile",
                                    "sram": 0.8,
                                    "type": "generator",
                                    "flash": 168.0,
                                    "stack": 256,
                                    "latency": 5.389028225,
                                    "cycle_count": 7747.0,
                                    "num_features": 5,
                                    "num_iterations": 5,
                                },
                                "Mean Difference": {
                                    "name": "Mean Difference",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 386.0,
                                    "stack": 244,
                                    "latency": 366.0,
                                    "cycle_count": 4392.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "100th Percentile": {
                                    "name": "100th Percentile",
                                    "sram": 0.8,
                                    "type": "generator",
                                    "flash": 168.0,
                                    "stack": 256,
                                    "latency": 2.153109436,
                                    "cycle_count": 7808.0,
                                    "num_features": 2,
                                    "num_iterations": 2,
                                },
                                "Dominant Frequency": {
                                    "name": "Dominant Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 668.0,
                                    "stack": 448,
                                    "latency": 36600.0,
                                    "cycle_count": 0.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Global Min Max Sum": {
                                    "name": "Global Min Max Sum",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 100,
                                    "stack": 292,
                                    "latency": 0.0,
                                    "cycle_count": 13786.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Global Peak to Peak": {
                                    "name": "Global Peak to Peak",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 285.0,
                                    "stack": 420,
                                    "latency": 14640.0,
                                    "cycle_count": 13664.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Interquartile Range": {
                                    "name": "Interquartile Range",
                                    "sram": 0.8,
                                    "type": "generator",
                                    "flash": 232.0,
                                    "stack": 272,
                                    "latency": 1098.0,
                                    "cycle_count": 35075.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Linear Regression Stats": {
                                    "name": "Linear Regression Stats",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 18,
                                    "num_iterations": 6,
                                },
                                "Negative Zero Crossings": {
                                    "name": "Negative Zero Crossings",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 5,
                                    "num_iterations": 5,
                                },
                                "Positive Zero Crossings": {
                                    "name": "Positive Zero Crossings",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Absolute Area of Spectrum": {
                                    "name": "Absolute Area of Spectrum",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 136,
                                    "stack": 184,
                                    "latency": 5856.0,
                                    "cycle_count": 8113.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Two Column Mean Difference": {
                                    "name": "Two Column Mean Difference",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 9,
                                    "num_iterations": 9,
                                },
                                "Total Area of Low Frequency": {
                                    "name": "Total Area of Low Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 251.6,
                                    "stack": 394,
                                    "latency": 2.578798668,
                                    "cycle_count": 3294.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Total Area of High Frequency": {
                                    "name": "Total Area of High Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 251.6,
                                    "stack": 394,
                                    "latency": 3.8583690720000003,
                                    "cycle_count": 4697.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Two Column Median Difference": {
                                    "name": "Two Column Median Difference",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 9,
                                    "num_iterations": 9,
                                },
                                "Two Column Min Max Difference": {
                                    "name": "Two Column Min Max Difference",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 15,
                                    "num_iterations": 15,
                                },
                                "Absolute Area of Low Frequency": {
                                    "name": "Absolute Area of Low Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 251.6,
                                    "stack": 364,
                                    "latency": 2.578441452,
                                    "cycle_count": 4697.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Absolute Area of High Frequency": {
                                    "name": "Absolute Area of High Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 273.6,
                                    "stack": 364,
                                    "latency": 3.8576542739999997,
                                    "cycle_count": 4514.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Two Column Peak To Peak Difference": {
                                    "name": "Two Column Peak To Peak Difference",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 13,
                                    "num_iterations": 13,
                                },
                                "Threshold With Offset Crossing Rate": {
                                    "name": "Threshold With Offset Crossing Rate",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Two Column Peak Location Difference": {
                                    "name": "Two Column Peak Location Difference",
                                    "sram": 0,
                                    "type": "generator",
                                    "flash": 0,
                                    "stack": 0,
                                    "latency": 0.0,
                                    "cycle_count": 0.0,
                                    "num_features": 15,
                                    "num_iterations": 15,
                                },
                                "Global Peak to Peak of Low Frequency": {
                                    "name": "Global Peak to Peak of Low Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 283.0,
                                    "stack": 406,
                                    "latency": 2.1430419350000003,
                                    "cycle_count": 9455.0,
                                    "num_features": 5,
                                    "num_iterations": 5,
                                },
                                "Global Peak to Peak of High Frequency": {
                                    "name": "Global Peak to Peak of High Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 299.0,
                                    "stack": 406,
                                    "latency": 3.850863144,
                                    "cycle_count": 9943.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                                "Max Peak to Peak of first half of High Frequency": {
                                    "name": "Max Peak to Peak of first half of High Frequency",
                                    "sram": 0.0,
                                    "type": "generator",
                                    "flash": 307.0,
                                    "stack": 406,
                                    "latency": 1.9372266539999998,
                                    "cycle_count": 9394.0,
                                    "num_features": 6,
                                    "num_iterations": 6,
                                },
                            },
                        },
                        {
                            "name": "Min Max Scale",
                            "sram": 0,
                            "type": "transform",
                            "flash": 312,
                            "stack": 176,
                            "latency": 1037.0,
                            "cycle_count": 830820.0,
                        },
                    ],
                    "framework": {
                        "sram": 610,
                        "flash": 1942,
                        "stack": 108,
                        "latency": 61,
                        "cycle_count": 0,
                    },
                    "classifier": {
                        "sram": 4224,
                        "flash": 36773,
                        "stack": 384,
                        "cmnsis_nn": {
                            "layers": [
                                {
                                    "ops": 58304,
                                    "macs": 29056,
                                    "time": 0.001455912607440229,
                                    "index": 0,
                                    "energy": 1.0399524563404767e-06,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 116473.00859521831,
                                    "input_shape": "1x454,64x454,64",
                                    "output_shape": "1x64",
                                },
                                {
                                    "ops": 4192,
                                    "macs": 2048,
                                    "time": 0.00012285022529051623,
                                    "index": 1,
                                    "energy": 6.854209145882362e-08,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 9828.018023241299,
                                    "input_shape": "1x64,32x64,32",
                                    "output_shape": "1x32",
                                },
                                {
                                    "ops": 1072,
                                    "macs": 512,
                                    "time": 4.434936447695015e-05,
                                    "index": 2,
                                    "energy": 1.74976825452745e-08,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 3547.949158156012,
                                    "input_shape": "1x32,16x32,16",
                                    "output_shape": "1x16",
                                },
                                {
                                    "ops": 280,
                                    "macs": 128,
                                    "time": 2.242998565795761e-05,
                                    "index": 3,
                                    "energy": 1.74976825452745e-08,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 1794.3988526366086,
                                    "input_shape": "1x16,8x16,8",
                                    "output_shape": "1x8",
                                },
                                {
                                    "ops": 102,
                                    "macs": 48,
                                    "time": 1.8755725066326873e-05,
                                    "index": 4,
                                    "energy": 1.74976825452745e-08,
                                    "opcode": "fully_connected",
                                    "options": "Activation:none",
                                    "cpu_cycles": 1500.4580053061497,
                                    "input_shape": "1x8,6x8,6",
                                    "output_shape": "1x6",
                                },
                                {
                                    "ops": 30,
                                    "macs": 0,
                                    "time": 6.549147727272728e-05,
                                    "index": 5,
                                    "energy": 1.652612450681789e-08,
                                    "opcode": "softmax",
                                    "options": "BuiltinOptionsType=9",
                                    "cpu_cycles": 5239.318181818182,
                                    "input_shape": "1x6",
                                    "output_shape": "1x6",
                                },
                            ],
                            "summary": {
                                "ops": 63980,
                                "macs": 31792,
                                "name": "my_model",
                                "time": 0.001729789385204707,
                                "energy": 1.1775137199419418e-06,
                                "j_per_op": 1.84044032501085e-11,
                                "n_layers": 6,
                                "op_per_s": 36987161.874870956,
                                "j_per_mac": 3.7038051080207027e-11,
                                "mac_per_s": 18379116.135134377,
                                "cpu_cycles": 138383.15081637655,
                                "accelerator": "None",
                                "inf_per_sec": 578.1050621267733,
                                "input_dtype": "int8",
                                "input_shape": "1x454",
                                "tflite_size": 36640,
                                "output_dtype": "int8",
                                "output_shape": "1x6",
                                "cpu_clock_rate": 80000000,
                                "cpu_utilization": 100.0,
                                "runtime_memory_size": 2080,
                                "n_unsupported_layers": 0,
                            },
                            "layer_labels": {
                                "ops": "# Ops",
                                "macs": "# MACs",
                                "time": "Time (s)",
                                "index": "Index",
                                "energy": "Energy (J)",
                                "opcode": "OpCode",
                                "options": "Options",
                                "cpu_cycles": "CPU Cycles",
                                "input_shape": "Input Shape",
                                "output_shape": "Output Shape",
                            },
                            "summary_labels": {
                                "ops": "# Operations",
                                "macs": "# Multiply-Accumulates",
                                "name": "Name",
                                "time": "Time (s)",
                                "energy": "Energy (J)",
                                "j_per_op": "J/Op",
                                "n_layers": "# Layers",
                                "op_per_s": "Ops/s",
                                "j_per_mac": "J/MAC",
                                "mac_per_s": "MACs/s",
                                "cpu_cycles": "# CPU Cycles",
                                "accelerator": "Accelerator",
                                "inf_per_sec": "Inference/s",
                                "input_dtype": "Input Data Type",
                                "input_shape": "Input Shape",
                                "tflite_size": "Model File Size (bytes)",
                                "output_dtype": "Output Data Type",
                                "output_shape": "Output Shape",
                                "cpu_clock_rate": "Clock Rate (hz)",
                                "cpu_utilization": "CPU Utilization (%)",
                                "runtime_memory_size": "Runtime Memory Size (bytes)",
                                "n_unsupported_layers": "# Unsupported Layers",
                            },
                        },
                        "cycle_count": 138383,
                        "silicon_labs_mvp": {
                            "layers": [
                                {
                                    "ops": 58304,
                                    "macs": 29056,
                                    "time": 0.0007296,
                                    "index": 0,
                                    "energy": 9.98191777066404e-07,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 1921.1865653770424,
                                    "input_shape": "1x454,64x454,64",
                                    "output_shape": "1x64",
                                    "accelerator_cycles": 58368,
                                },
                                {
                                    "ops": 4192,
                                    "macs": 2048,
                                    "time": 5.28e-05,
                                    "index": 1,
                                    "energy": 1.346185433819714e-07,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 1763.7233664655312,
                                    "input_shape": "1x64,32x64,32",
                                    "output_shape": "1x32",
                                    "accelerator_cycles": 4224,
                                },
                                {
                                    "ops": 1072,
                                    "macs": 512,
                                    "time": 2.046760149213518e-05,
                                    "index": 2,
                                    "energy": 4.9220259590463584e-08,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 1637.4081193708146,
                                    "input_shape": "1x32,16x32,16",
                                    "output_shape": "1x16",
                                    "accelerator_cycles": 1088,
                                },
                                {
                                    "ops": 280,
                                    "macs": 128,
                                    "time": 1.952950424619816e-05,
                                    "index": 3,
                                    "energy": 3.715482532156943e-08,
                                    "opcode": "fully_connected",
                                    "options": "Activation:relu",
                                    "cpu_cycles": 1562.3603396958529,
                                    "input_shape": "1x16,8x16,8",
                                    "output_shape": "1x8",
                                    "accelerator_cycles": 288,
                                },
                                {
                                    "ops": 102,
                                    "macs": 48,
                                    "time": 2.0680752036180876e-05,
                                    "index": 4,
                                    "energy": 4.9025006336730815e-09,
                                    "opcode": "fully_connected",
                                    "options": "Activation:none",
                                    "cpu_cycles": 1654.46016289447,
                                    "input_shape": "1x8,6x8,6",
                                    "output_shape": "1x6",
                                    "accelerator_cycles": 120,
                                },
                                {
                                    "ops": 30,
                                    "macs": 0,
                                    "time": 6.549147727272728e-05,
                                    "index": 5,
                                    "energy": 1.652612450681789e-08,
                                    "opcode": "softmax",
                                    "options": "BuiltinOptionsType=9",
                                    "cpu_cycles": 5239.318181818182,
                                    "input_shape": "1x6",
                                    "output_shape": "1x6",
                                    "accelerator_cycles": 0,
                                },
                            ],
                            "summary": {
                                "ops": 63980,
                                "macs": 31792,
                                "name": "my_model",
                                "time": 0.0009085693350472415,
                                "energy": 1.2406140305008992e-06,
                                "j_per_op": 1.939065380589089e-11,
                                "n_layers": 6,
                                "op_per_s": 70418401.25131819,
                                "j_per_mac": 3.9022836892957324e-11,
                                "mac_per_s": 34991275.59521581,
                                "cpu_cycles": 13778.456735621892,
                                "accelerator": "mvp",
                                "inf_per_sec": 1100.6314668852483,
                                "input_dtype": "int8",
                                "input_shape": "1x454",
                                "tflite_size": 36640,
                                "output_dtype": "int8",
                                "output_shape": "1x6",
                                "cpu_clock_rate": 80000000,
                                "cpu_utilization": 18.956253810428066,
                                "accelerator_cycles": 64088,
                                "runtime_memory_size": 2880,
                                "n_unsupported_layers": 0,
                            },
                            "layer_labels": {
                                "ops": "# Ops",
                                "macs": "# MACs",
                                "time": "Time (s)",
                                "index": "Index",
                                "energy": "Energy (J)",
                                "opcode": "OpCode",
                                "options": "Options",
                                "cpu_cycles": "CPU Cycles",
                                "input_shape": "Input Shape",
                                "output_shape": "Output Shape",
                                "accelerator_cycles": "Acc Cycles",
                            },
                            "summary_labels": {
                                "ops": "# Operations",
                                "macs": "# Multiply-Accumulates",
                                "name": "Name",
                                "time": "Time (s)",
                                "energy": "Energy (J)",
                                "j_per_op": "J/Op",
                                "n_layers": "# Layers",
                                "op_per_s": "Ops/s",
                                "j_per_mac": "J/MAC",
                                "mac_per_s": "MACs/s",
                                "cpu_cycles": "# CPU Cycles",
                                "accelerator": "Accelerator",
                                "inf_per_sec": "Inference/s",
                                "input_dtype": "Input Data Type",
                                "input_shape": "Input Shape",
                                "tflite_size": "Model File Size (bytes)",
                                "output_dtype": "Output Data Type",
                                "output_shape": "Output Shape",
                                "cpu_clock_rate": "Clock Rate (hz)",
                                "cpu_utilization": "CPU Utilization (%)",
                                "accelerator_cycles": "# Accelerator Cycles",
                                "runtime_memory_size": "Runtime Memory Size (bytes)",
                                "n_unsupported_layers": "# Unsupported Layers",
                            },
                        },
                    },
                },
            )
        )

    return knowledgepacks


def find(name, kpList):
    for kp in kpList:
        if kp.name == name:
            return kp
    return None


@pytest.mark.usefixtures("authenticate")
def test_knowledge_packs(client, project, sandbox, knowledgepacks):
    import time

    start = time.time()
    response = client.get(
        reverse(
            "knowledgepack-list-project", kwargs={"project_uuid": str(project.uuid)}
        )
    )
    print(time.time() - start)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 10

    result1 = response.data[0]
    kp = find(result1["name"], knowledgepacks)
    assert result1["sandbox_name"] == sandbox.name
    assert result1["project_name"] == project.name
    assert result1["accuracy"] == kp.model_results["metrics"]["validation"]["accuracy"]
    assert result1["features_count"] == len(kp.feature_summary)
    assert result1["classifier_name"] == "PME"
    assert result1["model_size"] == kp.model_results["model_size"]

    response = client.get(
        reverse("knowledgepack-detail-user", kwargs={"uuid": str(kp.uuid)})
    )
    result = response.json()
    assert result["neuron_array"] == {"model_parameters": True}

    url = reverse("knowledgepack-detail-user", kwargs={"uuid": str(kp.uuid)})
    response_filtered_fields = client.get(f"{url}?fields[]=uuid&fields[]=name")

    assert response_filtered_fields.json().get("neuron_array") == None

    response_omitted_fields = client.get(f"{url}?omit_fields[]=name")

    assert response_omitted_fields.json().get("name") == None
    assert response_omitted_fields.json().get("neuron_array") == {
        "model_parameters": True
    }

    sandbox_detail_url = reverse(
        "sandbox-detail", kwargs={"project_uuid": project.uuid, "uuid": sandbox.uuid}
    )

    response = client.delete(sandbox_detail_url)

    response = client.get(
        reverse("knowledgepack-detail-user", kwargs={"uuid": str(kp.uuid)})
    )

    assert response.json()["sandbox_uuid"] == None


@pytest.mark.usefixtures("authenticate")
def test_knowledge_log_view(client, project, sandbox, knowledgepacks):
    for kp in knowledgepacks[:2]:
        kp_dir = os.path.join(settings.SERVER_CODEGEN_ROOT, str(kp.uuid))

        if not os.path.exists(kp_dir):
            os.mkdir(kp_dir)

        with open(os.path.join(kp_dir, "{}_build.log".format(kp.uuid)), "w") as out:
            out.write("test kp log file")

        response = client.get(
            reverse(
                "knowledge-pack-build-logs-view",
                kwargs={"uuid": str(kp.uuid)},
            )
        )

        assert response.status_code == status.HTTP_200_OK

        try:
            shutil.rmtree(kp_dir)
        except OSError as e:
            print("Error: %s : %s" % (kp_dir, e.strerror))


@pytest.mark.usefixtures("authenticate")
def test_knowledgepack_resource_summary(client, project, knowledgepacks):
    response = client.get(
        reverse(
            "report-view",
            kwargs={
                "project_uuid": project.uuid,
                "uuid": str(knowledgepacks[0].uuid),
                "report_type": "resource_summary",
            },
        ),
        {"accelerator": "cmsis_nn"},
    )

    expected_result = {
        "sram": 5736,
        "flash": 56358,
        "stack": 1384,
        "max_segment_length": 61.0,
        "clock_speed_mhz": 80,
        "classifier_cycle_count": 138383,
        "feature_cycle_count": 1447443,
        "feature_time_us": 18093.037,
        "feature_time_ms": 18.093037,
        "classifier_time_us": 1729.787,
        "classifier_time_ms": 1.729788,
    }

    assert json.loads(response.json()) == expected_result

    response = client.get(
        reverse(
            "report-view",
            kwargs={
                "project_uuid": project.uuid,
                "uuid": str(knowledgepacks[0].uuid),
                "report_type": "resource_summary",
            },
        ),
        {"accelerator": "silicon_labs_mvp"},
    )

    expected_result = {
        "sram": 5736,
        "flash": 56358,
        "stack": 1384,
        "max_segment_length": 61.0,
        "clock_speed_mhz": 80,
        "classifier_cycle_count": 13778,
        "feature_cycle_count": 1447443,
        "feature_time_us": 18093.037,
        "feature_time_ms": 18.093037,
        "classifier_time_us": 172.225,
        "classifier_time_ms": 0.172225,
    }

    assert json.loads(response.json()) == expected_result


@pytest.mark.usefixtures("authenticate")
def test_create_knowledge_packs(client, project):
    feature_summary = [
        {
            "Feature": "gen_0010_GXAY_cross_mean_diff",
            "Sensors": ["GyroscopeX", "AccelerometerY"],
            "Category": "Column Fusion",
            "Generator": "Two Column Mean Difference",
            "LibraryPack": None,
            "ContextIndex": 9,
            "EliminatedBy": None,
            "GeneratorIndex": 4,
            "GeneratorTrueIndex": 10,
            "GeneratorFamilyIndex": 0,
            "GeneratorFamilyFeatures": 1,
        }
    ]

    data = {
        "project": project.uuid,
        "pipeline_summary": [],
        "query_summary": [],
        "feature_summary": feature_summary,
        "class_map": {1: "red", 2: "blue"},
        "sensor_summary": [],
        "transform_summary": [],
        "knowledgepack_summary": [],
        "sandbox": None,
        "name": "TEST KP",
        "model_parameters": [],
        "model_configuration": {"classifier": "bonsai"},
    }
    response = client.post(
        reverse(
            "knowledgepack-list-project", kwargs={"project_uuid": str(project.uuid)}
        ),
        data=data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.usefixtures("authenticate")
def test_create_export_knowledge_packs(client, project):
    for model in ["tf", "pme", "dte", "bonsai"]:
        model_data = json.load(
            open(
                os.path.join(
                    os.path.dirname(__file__), "data", f"export_{model}_model.json"
                ),
                "r",
            )
        )
        model_data["project"] = project.uuid

        response = client.post(
            reverse(
                "knowledgepack-list-project", kwargs={"project_uuid": str(project.uuid)}
            ),
            data=model_data,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        uuid = response.json()["uuid"]

        response = client.get(
            reverse("knowledge-pack-export-view", kwargs={"uuid": str(uuid)}),
        )

        assert response.status_code == status.HTTP_200_OK
