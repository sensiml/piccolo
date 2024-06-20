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
model_id = "25cb9aa8-5e42-11ed-9b6a-0242ac120002"


def train():
    """Description of training process for this model"""


def load():
    """Loading foundation model into our local model zoo"""

    tf_model = load_model(
        os.path.join(
            os.path.dirname(__file__), "data", "mfcc23x49_w480_d320_dscnn_v02.h5"
        )
    )

    store_model_in_model_zoo(domain, model_id, tf_model)


def upload():
    """Upload the model to the model store"""

    params = {
        "description": "Google KW base model, DS-CNN, 25948 params.",
        "name": "mfcc23x49_w480_d320_dscnn_v02",
        "auxiliary_datafile": "Google_KW_mfcc23x49_w480_d320_scaled_pm50000.csv",
        "trainable_layer_groups": {
            "0": 0,
            "1": 9,
            "2": 15,
            "3": 21,
            "4": 27,
        },
        "model_profile": {
            "summary": {
                "name": "mfcc23x49_w480_d320_dscnn_v02",
                "accelerator": "None",
                "input_shape": "1x49x23x1",
                "input_dtype": "int8",
                "output_shape": "1x28",
                "output_dtype": "int8",
                "tflite_size": 49392,
                "runtime_memory_size": 46784,
                "ops": 13287912,
                "macs": 6376192,
                "n_layers": 13,
                "n_unsupported_layers": 0,
                "cpu_cycles": 30744893.916381836,
                "cpu_utilization": 0.0,
                "cpu_clock_rate": 78000000,
                "energy": 0.00576025136481917,
                "j_per_op": 4.33495598467176e-10,
                "j_per_mac": 9.033999234682973e-10,
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
                    "ops": 1593600,
                    "macs": 768000,
                    "cpu_cycles": 7784981.5,
                    "energy": 0.00149083964060992,
                    "input_shape": "1x49x23x1,64x10x4x1,64",
                    "output_shape": "1x25x12x64",
                    "options": "Padding:same stride:2x2 activation:relu",
                },
                {
                    "index": 1,
                    "opcode": "depthwise_conv_2d",
                    "ops": 403200,
                    "macs": 172800,
                    "cpu_cycles": 2099782.25,
                    "energy": 0.00041543738916516304,
                    "input_shape": "1x25x12x64,1x3x3x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 2,
                    "opcode": "conv_2d",
                    "ops": 2515200,
                    "macs": 1228800,
                    "cpu_cycles": 3614083.75,
                    "energy": 0.0006517791771329939,
                    "input_shape": "1x25x12x64,64x1x1x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 3,
                    "opcode": "depthwise_conv_2d",
                    "ops": 403200,
                    "macs": 172800,
                    "cpu_cycles": 2099782.25,
                    "energy": 0.00041543738916516304,
                    "input_shape": "1x25x12x64,1x3x3x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 4,
                    "opcode": "conv_2d",
                    "ops": 2515200,
                    "macs": 1228800,
                    "cpu_cycles": 3614083.75,
                    "energy": 0.0006517791771329939,
                    "input_shape": "1x25x12x64,64x1x1x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 5,
                    "opcode": "depthwise_conv_2d",
                    "ops": 403200,
                    "macs": 172800,
                    "cpu_cycles": 2099782.25,
                    "energy": 0.00041543738916516304,
                    "input_shape": "1x25x12x64,1x3x3x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 6,
                    "opcode": "conv_2d",
                    "ops": 2515200,
                    "macs": 1228800,
                    "cpu_cycles": 3614083.75,
                    "energy": 0.0006517791771329939,
                    "input_shape": "1x25x12x64,64x1x1x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 7,
                    "opcode": "depthwise_conv_2d",
                    "ops": 403200,
                    "macs": 172800,
                    "cpu_cycles": 2099782.25,
                    "energy": 0.00041543738916516304,
                    "input_shape": "1x25x12x64,1x3x3x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Multiplier:1 padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 8,
                    "opcode": "conv_2d",
                    "ops": 2515200,
                    "macs": 1228800,
                    "cpu_cycles": 3614083.75,
                    "energy": 0.0006517791771329939,
                    "input_shape": "1x25x12x64,64x1x1x64,64",
                    "output_shape": "1x25x12x64",
                    "options": "Padding:same stride:1x1 activation:relu",
                },
                {
                    "index": 9,
                    "opcode": "average_pool_2d",
                    "ops": 16960,
                    "macs": 0,
                    "cpu_cycles": 87953.625,
                    "energy": 4.785296141562867e-07,
                    "input_shape": "1x25x12x64",
                    "output_shape": "1x1x1x64",
                    "options": "Padding:valid stride:11x24 filter:11x24 activation:none",
                },
                {
                    "index": 10,
                    "opcode": "reshape",
                    "ops": 0,
                    "macs": 0,
                    "cpu_cycles": 264.8948974609375,
                    "energy": 4.810656518903605e-19,
                    "input_shape": "1x1x1x64,2",
                    "output_shape": "1x64",
                    "options": "Type=none",
                },
                {
                    "index": 11,
                    "opcode": "fully_connected",
                    "ops": 3612,
                    "macs": 1792,
                    "cpu_cycles": 8564.2978515625,
                    "energy": 5.040327977212655e-08,
                    "input_shape": "1x64,28x64,28",
                    "output_shape": "1x28",
                    "options": "Activation:none",
                },
                {
                    "index": 12,
                    "opcode": "softmax",
                    "ops": 140,
                    "macs": 0,
                    "cpu_cycles": 7665.5986328125,
                    "energy": 1.6526122692539502e-08,
                    "input_shape": "1x28",
                    "output_shape": "1x28",
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
