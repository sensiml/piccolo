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

from library.model_zoo import store_model_in_model_zoo, upload_model_as_foundation_model
from tensorflow.keras.models import load_model

"""
Require:
    Description of the inputs
    Description of the model

Load model from local files
Upload Model to DataBase as a KnowledgePack

Use models as part of Pipeline Templates

Future: Create List API for description of Transfer Learning Models to show in the UI

"""

domain = "kw_spotting"
model_id = "db617dac-aa3c-4db4-8dd0-a2655f4f6fc9"


def train():
    """Description of training process for this model"""


def load():
    """Loading foundation model into our local model zoo"""

    tf_model = load_model(
        os.path.join(
            os.path.dirname(__file__), "data", "mfcc1127_t49x16_dscnn_filt16_v01.h5"
        )
    )

    store_model_in_model_zoo(domain, model_id, tf_model)


def upload():
    """Upload the model to the model store"""

    params = {
        "description": "Google KW base model, DS-CNN, 3786 params.",
        "name": "mfcc1127_t49x16_dscnn_filt16_v01",
        "auxiliary_datafile": "Google_KW_mfcc23x49_trimmed16x49_w480_d320_scaled_pm50000.csv",
        "trainable_layer_groups": {
            "0": 0,
            "1": 9,
            "2": 15,
            "3": 21,
            "4": 27,
        },
        "model_profile": {
            "summary": {
                "name": "mfcc1127_t49x16_dscnn_filt16_v01",
                "accelerator": "None",
                "input_shape": "1x49x16x1",
                "input_dtype": "int8",
                "output_shape": "1x2",
                "output_dtype": "int8",
                "tflite_size": 20056,
                "runtime_memory_size": 10764,
                "ops": 1037948,
                "macs": 474144,
                "n_layers": 16,
                "n_unsupported_layers": 0,
                "cpu_cycles": 4255080.594604492,
                "cpu_utilization": 0.0,
                "cpu_clock_rate": 78000000,
                "energy": 0.000380855348391052,
                "j_per_op": 3.66931048945662e-10,
                "j_per_mac": 8.03248271392345e-10,
            },
            "summary_labels": {
                "name": "Name",
                "accelerator": "Accelerator",
                "input_shape": "Input Shape",
                "input_dtype": "Input Data Type",
                "output_shape": "Output Shape",
                "output_dtype": "Output Data Type",
                "tflite_size": "Flash, Model File Size (bytes)",
                "runtime_memory_size": "RAM, Runtime Memory Size (bytes)",
                "ops": "Operation Count",
                "macs": "Multiply-Accumulate Count",
                "n_layers": "Layer Count",
                "n_unsupported_layers": "Unsupported Layer Count",
                "cpu_cycles": "CPU Cycle Count",
                "cpu_utilization": "CPU Utilization (%)",
                "cpu_clock_rate": "Clock Rate (hz)",
                "energy": "Energy (J)",
                "j_per_op": "J/Op",
                "j_per_mac": "J/MAC",
            },
            "layers": [
                {
                    "index": 0,
                    "opcode": "conv_2d",
                    "ops": 316800,
                    "macs": 153600,
                    "cpu_cycles": 1779106.375,
                    "energy": 6.405382737284526e-05,
                    "input_shape": "1x49x16x1,16x12x4x1,16",
                    "output_shape": "1x25x8x16",
                    "options": "Padding:same stride:2x2 activation:relu",
                },
                {
                    "index": 1,
                    "opcode": "depthwise_conv_2d",
                    "ops": 67200,
                    "macs": 28800,
                    "cpu_cycles": 331847.5625,
                    "energy": 3.9059825212461874e-05,
                    "input_shape": "1x25x8x16,1x3x3x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 2,
                    "opcode": "conv_2d",
                    "ops": 112000,
                    "macs": 51200,
                    "cpu_cycles": 266938.84375,
                    "energy": 3.82883517886512e-05,
                    "input_shape": "1x25x8x16,16x1x1x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 3,
                    "opcode": "depthwise_conv_2d",
                    "ops": 67200,
                    "macs": 28800,
                    "cpu_cycles": 331847.5625,
                    "energy": 3.9059825212461874e-05,
                    "input_shape": "1x25x8x16,1x3x3x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 4,
                    "opcode": "conv_2d",
                    "ops": 112000,
                    "macs": 51200,
                    "cpu_cycles": 266938.84375,
                    "energy": 3.82883517886512e-05,
                    "input_shape": "1x25x8x16,16x1x1x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 5,
                    "opcode": "depthwise_conv_2d",
                    "ops": 67200,
                    "macs": 28800,
                    "cpu_cycles": 331847.5625,
                    "energy": 3.9059825212461874e-05,
                    "input_shape": "1x25x8x16,1x3x3x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 6,
                    "opcode": "conv_2d",
                    "ops": 112000,
                    "macs": 51200,
                    "cpu_cycles": 266938.84375,
                    "energy": 3.82883517886512e-05,
                    "input_shape": "1x25x8x16,16x1x1x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 7,
                    "opcode": "depthwise_conv_2d",
                    "ops": 67200,
                    "macs": 28800,
                    "cpu_cycles": 331847.5625,
                    "energy": 3.9059825212461874e-05,
                    "input_shape": "1x25x8x16,1x3x3x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 8,
                    "opcode": "conv_2d",
                    "ops": 112000,
                    "macs": 51200,
                    "cpu_cycles": 266938.84375,
                    "energy": 3.82883517886512e-05,
                    "input_shape": "1x25x8x16,16x1x1x16,16",
                    "output_shape": "1x25x8x16",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 9,
                    "opcode": "average_pool_2d",
                    "ops": 3088,
                    "macs": 0,
                    "cpu_cycles": 58580.26953125,
                    "energy": 6.917385235283291e-06,
                    "input_shape": "1x25x8x16",
                    "output_shape": "1x1x1x16",
                    "options": "Padding:valid stride:8x24 filter:8x24 activation:none",
                },
                {
                    "index": 10,
                    "opcode": "quantize",
                    "ops": 64,
                    "macs": 0,
                    "cpu_cycles": 11898.5537109375,
                    "energy": 4.2240858988407126e-07,
                    "input_shape": "1x1x1x16",
                    "output_shape": "1x1x1x16",
                    "options": "Type=none",
                },
                {
                    "index": 11,
                    "opcode": "reshape",
                    "ops": 0,
                    "macs": 0,
                    "cpu_cycles": 264.8948974609375,
                    "energy": 4.810656518903605e-19,
                    "input_shape": "1x1x1x16,2",
                    "output_shape": "1x16",
                    "options": "Type=none",
                },
                {
                    "index": 12,
                    "opcode": "fully_connected",
                    "ops": 560,
                    "macs": 256,
                    "cpu_cycles": 2671.423828125,
                    "energy": 1.7497688631351593e-08,
                    "input_shape": "1x16,16x16,16",
                    "output_shape": "1x16",
                    "options": "Activation:relu",
                },
                {
                    "index": 13,
                    "opcode": "fully_connected",
                    "ops": 560,
                    "macs": 256,
                    "cpu_cycles": 2671.423828125,
                    "energy": 1.7497688631351593e-08,
                    "input_shape": "1x16,16x16,16",
                    "output_shape": "1x16",
                    "options": "Activation:relu",
                },
                {
                    "index": 14,
                    "opcode": "fully_connected",
                    "ops": 66,
                    "macs": 32,
                    "cpu_cycles": 903.61083984375,
                    "energy": 1.7497688631351593e-08,
                    "input_shape": "1x16,2x16,2",
                    "output_shape": "1x2",
                    "options": "Activation:none",
                },
                {
                    "index": 15,
                    "opcode": "softmax",
                    "ops": 10,
                    "macs": 0,
                    "cpu_cycles": 3838.41796875,
                    "energy": 1.6526122692539502e-08,
                    "input_shape": "1x2",
                    "output_shape": "1x2",
                    "options": "Type=softmaxoptions",
                },
            ],
            "layer_labels": {
                "index": "Index",
                "opcode": "OpCode",
                "ops": "# Ops",
                "macs": "# MACs",
                "cpu_cycles": "CPU Cycles",
                "energy": "Energy (J)",
                "input_shape": "Input Shape",
                "output_shape": "Output Shape",
                "options": "Options",
            },
        },
    }

    upload_model_as_foundation_model(domain, model_id, params)
