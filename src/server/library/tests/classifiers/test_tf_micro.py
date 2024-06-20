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

import binascii

import numpy as np
import pytest
from library.classifiers.tensorflow_micro import TensorFlowMicro
from pandas import DataFrame

# pytestmark = pytest.mark.django_db  # All tests use db

# fmt: off

@pytest.fixture
def model_parameters_regression():
    return {
        "tflite": "1800000054464c3300000e001800040008000c00100014000e00000003000000ec090000b8050000a0050000040000000b000000900500007c05000024050000d4040000cc040000c4040000bc0400006c0400005c0000000c0000000400000078f6ffffb6faffff040000004000000030779c3d01a8053f2b55ec3e2b8211bf57e3803e960cf3bebf930dbf905899bd9068a8bde424f6bd23a1333e08b398bdcf45173ed4f7953e524e0bbe825ad2be02fbffff04000000000400005a733b3e5e0565be9df39b3e80d2debcd8b5b1beead80c3e186bfdbd24c883becc8a8c3d0a78583eeebf963e6bf2b83e35c032be9877f83c8af181be6476cb3d7e339cbedd5777be79ef9a3ca622383e17c1c43e98369ebd0e9e4a3e4a2d5f3eb1ce9f3e68e129bd90992abde48615beecbba4bd807a5cbbaae37e3eaa46713e178a863e084980bdfc7206be0ac24d3e5c6cdc3ddf2fdc3e6da8b83e9a27bfbebc07cabd40c8933b1a753d3e68007d3d087d6cbd0b5a9cbe819b9b3ec331d83ede4825be18aca3bea6b823be3a885f3e00f1d5be61508cbefe65acbee0a15bbcc4fbfd3d93e5b73ea1ddd3beb01b71be3dafca3e249d973d89d4853ea077233c35c4a1be48ec6b3e062b7cbee52bd13ef941cbbe10f3583d3ae92e3e747697bd1958d93efa8e2c3e0ed2703e008055385e8e993d3e1d843ea17ab13ea89400bdfc05a7bdfdaf403d64c8313e717fc53e6635a6be18443ebd05baabbe57708a3e78001dbd20ddcdbc2a637a3ecd67bdbe028084bee8ae73be52fe233e7dc366bed7e6353ef8772bbea704a23ea0358b3c60c48c3e102f8fbd702948bd3e7909bec2ff59be53f3ccbecce7723e18c35d3d7ad5acbe4f830cbe9264633ef86bbdbeb0db313e501ea7bee286e43d6578c53ece2d3f3e95108b3e4d8eb83ea9d4d63e3768cc3e6c0583be6089fdbc4b1347be3091223d15ebdfbe46588dbea5c5b03ea3a51ebe7d482c3edd2db73eca667b3e76bf13be40197fbc2ba63dbe6dc883be4fa383bec0f4f63b1d3a9bbeece49abe2252c4be13be89bdc7c0a73e9078d7bd5034d93e249ea4be8f3dd6bd60cc393db81bd43eb10ab8be39f667bef25db4bee05d22bdab47cd3e3538c8bc86ce0fbe1a18c9bd3440e03e28ff1cbef64a193efd3f92bed775743e45eae0bdaa5f1dbe14a0993e7082b73c1b3d9d3e2d778d3eff62b53e92be82be702d2ebd2589a63e24f5df3d4902d6be9ea75fbef5e0923e9bda1cbe5a57f93df4c92f3ea49d983d6a599ebe6b82943e805a613d3f30c6bea869d5be0664b2beb2579dbe7318ad3eb22c773ee7e5c33ef523853ec357afbecd3dacbe3618d4bdc281f63d3fd9a03ef888c5be91b7d1be3371933e3a01a2be7b9dda3ee3b1b5be5dc3e9bd49eb81be619cbd3e8e9b883ecb8ed83e30ccb7be16928e3ee21a93bdc05a593e1ce79ebd1121b43e8b509c3e322f443e8a32a0bef6291b3e583211bdc2ac0f3e503051bd4a1fe33dbf3b533d644ccb3d03e1973ef36ca3beff358d3e70dcce3e4450e33d08dd80be09b6cc3e0064d7bd8ae55c3e345cf13d89f7ab3e1c97c13eedaf3bbe6da59f3e04d492be6097a23cc117d13ea9e577be1eb813bdb9e6a83c126c603ebc2ac0be8008c1bc948717bec2da3c3e5ce9a2be960e0f3e719be7bed295adbe2daeb23d4280853ecc78e3bd34e7a6be0effffff0400000040000000f83a583e48304fbb0000000000000000da3172be044a4abc09b66abe8acb0dbc178f663e749e663e88da3bbec4d569be0ce3d13d1a6769be1db1663ea6b75fbd20fbffff24fbffff28fbffff66ffffff0400000040000000cf37383e3b114dbe9885763e0000000049e66ebe000000000000000000000000000000000000000090d368be000000000d9979befbae133e0000000000000000b2ffffff04000000400000007b0514bf96738a3ddc92c5beba210d3f39bf73becef74d3ea8efa0be9273903e9fca863e8448b63e865364bed7ac1dbe7a846cbe5371a3be5f8cad3e6097cf3d00000600080004000600000004000000040000003615673edcfbffff0f000000544f434f20436f6e7665727465642e0001000000100000000c001400040008000c0010000c000000f0000000e4000000d80000000400000003000000900000004800000004000000ceffffff00000008180000000c0000000400000040fcffff01000000000000000300000007000000080000000900000000000e001400000008000c00070010000e000000000000081c0000001000000004000000baffffff0000000101000000070000000300000004000000050000000600000000000e001600000008000c00070010000e0000000000000824000000180000000c00000000000600080007000600000000000001010000000400000003000000010000000200000003000000010000000000000001000000010000000a000000ec0200008402000024020000dc0100009801000038010000f0000000ac0000004c000000040000004afdffff38000000010000000c000000040000003cfdffff1e00000073657175656e7469616c2f64656e73655f322f4d61744d756c5f62696173000001000000010000008efdffff4c000000020000000c0000000400000080fdffff3200000073657175656e7469616c2f64656e73655f322f4d61744d756c2f526561645661726961626c654f702f7472616e73706f73650000020000000100000010000000eafdffff30000000040000000c00000004000000dcfdffff1700000073657175656e7469616c2f64656e73655f312f52656c75000200000001000000100000002afeffff38000000070000000c000000040000001cfeffff1e00000073657175656e7469616c2f64656e73655f312f4d61744d756c5f62696173000001000000100000006efeffff4c000000080000000c0000000400000060feffff3200000073657175656e7469616c2f64656e73655f312f4d61744d756c2f526561645661726961626c654f702f7472616e73706f73650000020000001000000010000000cafeffff300000000a0000000c00000004000000bcfeffff1500000073657175656e7469616c2f64656e73652f52656c750000000200000001000000100000000affffff38000000030000000c00000004000000fcfeffff1c00000073657175656e7469616c2f64656e73652f4d61744d756c5f626961730000000001000000100000004effffff4c000000090000000c0000000400000040ffffff3000000073657175656e7469616c2f64656e73652f4d61744d756c2f526561645661726961626c654f702f7472616e73706f736500000000020000001000000001000000aaffffff44000000050000002c0000000c00000008000c00040008000800000010000000040000000100000000007f4301000000000000000b00000064656e73655f696e7075740002000000010000000100000000000e0014000400000008000c0010000e000000280000000600000010000000080000000400040004000000080000004964656e7469747900000000020000000100000001000000010000001000000000000a000c000700000008000a0000000000000903000000",
        "estimator_type": "regression",
        "tensor_arena_size":2048
    }


@pytest.fixture
def feature_vectors_regression():
    return DataFrame(
        [
            [1.61000000e02, -7.41544402e-01],
            [6.00000000e00, 2.56994899e-01],
            [6.40000000e01, 1.08497892e00],
            [6.00000000e00, 1.85012370e-01],
            [1.51000000e02, -4.19857279e-01],
            [3.30000000e01, 6.64991314e-01],
            [1.88000000e02, -8.30080403e-01],
            [1.03000000e02, 5.90643827e-01],
            [4.00000000e01, 9.02353208e-01],
            [2.02000000e02, -1.04080093e00],
            [5.80000000e01, 8.90452620e-01],
            [1.89000000e02, -1.00152093e00],
            [1.71000000e02, -8.99125367e-01],
            [6.50000000e01, 1.00057770e00],
            [1.37000000e02, 3.99664636e-03],
            [4.80000000e01, 1.06279939e00],
            [1.57000000e02, -6.42555810e-01],
            [6.40000000e01, 1.02473142e00],
            [2.19000000e02, -9.88742510e-01],
            [8.80000000e01, 8.52150032e-01],
            [2.03000000e02, -9.47187668e-01],
            [3.50000000e01, 7.54067292e-01],
            [2.48000000e02, -2.28358929e-01],
            [4.40000000e01, 9.28650578e-01],
        ]
    )


@pytest.fixture
def model_parameters_classification():
    return {
        "tflite": "1800000054464c3300000e001800040008000c00100014000e00000003000000a00800000c0000001000000020000000010000007c0100000f000000544f434f20436f6e7665727465642e000f00000050010000380100002001000018010000fc000000f4000000e0000000d8000000d0000000b4000000ac000000a4000000840000007c00000004000000eef7ffff0400000068000000451e2f3cac04663dbfba17be87995fbebc7723be276c423e46a3383ea720733ed7b870bebf699ebeef9d043b03e49dbd150f92bed9b34e3e6c8b953ef14699be49dd49be7162a13e9eee023e856c89be46590a3e2288e6bd692498be0ada363ef06887bd1987ba3c6cf9ffff66f8ffff040000001000000001000000010000001a000000010000008cf9ffff90f9ffff8af8ffff040000000c000000010000000100000002000000acf9ffffb0f9ffffaaf8ffff0400000004000000ac240b38c4f9ffffbef8ffff040000000c000000010000000100000001000000e0f9ffffdaf8ffff04000000080000002939ac3f96b216beeef8ffff0400000008000000f72753c04840ae3f0cfaffff0c001400040008000c0010000c000000200000001400000008000000f8040000010000000000000001000000010000000e0000002c03000048010000c40300009c01000084000000dc0000002000000058030000c4020000740200002402000060040000e8030000c4010000bafbffff100000000e0000001c000000480000000400000001000000010000001a000000010000002b00000073657175656e7469616c5f31312f636f6e7631645f31312f636f6e7631642f457870616e6444696d735f3100d4faffff16fcffff100000000d0000001c000000480000000400000001000000010000001a000000010000002900000073657175656e7469616c5f31312f636f6e7631645f31312f636f6e7631642f457870616e6444696d7300000030fbffff8afdffff00000002100000000c00000014000000440000000200000001000000040000002f00000073657175656e7469616c5f31312f636f6e7631645f31312f636f6e7631642f457870616e6444696d732f64696d5f30008cfbffffcefcffff100000000b000000180000003000000003000000010000001a000000010000000f000000636f6e7631645f31315f696e7075740008000c00040008000800000010000000040000000100000000007f4301000000000000002afdffff100000000a0000001c0000003c00000004000000010000000100000001000000010000001c00000073657175656e7469616c5f31312f636f6e7631645f31312f52656c750000000038fcffff92feffff000000021000000009000000100000003c00000001000000030000002900000073657175656e7469616c5f31312f64656e73655f31312f54656e736f72646f742f636f6e6361745f310000008cfcffffcefdffff100000000800000014000000380000000200000001000000020000002000000073657175656e7469616c5f31312f64656e73655f31312f54656e736f72646f7400000000d8fcffff1afeffff10000000070000001800000038000000030000000100000001000000020000001e00000073657175656e7469616c5f31312f64656e73655f31312f42696173416464000024fdffff66feffff1000000006000000100000003400000001000000010000002300000073657175656e7469616c5f31312f636f6e7631645f31312f636f6e7631645f62696173006cfdffffaefeffff1000000005000000180000002400000003000000010000000100000002000000080000004964656e7469747900000000ecfeffff00000e001800080007000c00100014000e000000000000021000000004000000100000004000000001000000030000002c00000073657175656e7469616c5f31312f636f6e7631645f31312f636f6e7631642f53717565657a655f7368617065000000000cfeffff4effffff10000000030000001800000038000000030000000100000001000000010000001f00000073657175656e7469616c5f31312f636f6e7631645f31312f426961734164640058feffff9affffff100000000200000014000000500000000200000002000000010000003400000073657175656e7469616c5f31312f64656e73655f31312f54656e736f72646f742f526573686170655f312f7472616e73706f736500000000040006000400000000000e0014000400000008000c0010000e0000001000000001000000100000004000000001000000020000002c00000073657175656e7469616c5f31312f64656e73655f31312f54656e736f72646f742f4d61744d756c5f626961730000000020ffffff06000000ac0100003c010000d800000094000000440000001800000014001400040008000c000000000000000000100014000000020000000c00000010000000140000000100000009000000010000000000000000000000bcfeffff000000110300000010000000180000002000000018000000020000000a0000000d000000010000000900000000000000a6feffff040000000300000001000000010000000200000008ffffff0000000801000000100000001c000000280000001c00000003000000020000000c0000000b000000010000000a00000000000000040004000400000048ffffff00000011030000001000000018000000200000001800000002000000030000000700000001000000020000000000000032ffffff040000000300000001000000010000000100000014001800000008000c00070010000000000014001400000000000002100000001c000000340000001c0000000300000004000000060000000800000001000000030000000000000000000e001400060008000c00100007000e0000000000010101000000010000000100000014001c0008000c0010000700140000000000180014000000000000110300000010000000180000002800000018000000020000000100000005000000010000000400000000000000000006000800040006000000040000000400000001000000010000001a0000000100000004000000340000001c000000080000000c000000d6ffffff0000000edeffffff00000016e6ffffff00000009faffffff00160600060005000600000000040600080007000600000000000016",
        "estimator_type": "classification",
    }


@pytest.fixture
def feature_vectors_classification():
    return DataFrame(
        [
            [80, 6, 1, 3, 9, 241, 253, 251, 253, 253, 253, 252, 2, 254, 253, 252, 252, 250, 245, 1, 2, 2, 1, 1, 1, 1, 1],
            [144, 3, 2, 4, 7, 248, 251, 252, 253, 252, 253, 252, 4, 253, 253, 253, 251, 251, 221, 2, 1, 1, 0, 0, 1, 2, 1],
            [67, 248, 252, 251, 247, 17, 4, 1, 2, 2, 1, 1, 252, 1, 1, 0, 3, 7, 31, 253, 254, 253, 253, 254, 253, 253, 2],
            [84, 248, 251, 250, 242, 13, 4, 0, 1, 0, 0, 1, 250, 0, 1, 2, 2, 5, 33, 253, 253, 253, 253, 253, 253, 253, 2],
        ]
    )

# fmt: on


def test_recongize_vector_with_regression(
    model_parameters_regression, feature_vectors_regression
):

    classifier = TensorFlowMicro(config={})

    classifier.load_model(model_parameters_regression)

    classifier.preprocess(1, feature_vectors_regression)

    results = classifier.recognize_vectors(package(feature_vectors_regression.values))

    assert np.mean(results["mean_squared_error"]["average"]) < 0.3


def test_recongize_vector_with_classification(
    model_parameters_classification, feature_vectors_classification
):

    classifier = TensorFlowMicro(config={})

    classifier.load_model(model_parameters_classification)

    classifier.preprocess(1, feature_vectors_classification)

    results = classifier.recognize_vectors(
        package(feature_vectors_classification.values), include_predictions=True
    )

    assert results["y_pred"] == [1, 1, 2, 2]


def test_recongize_vector_with_classification_threshold(
    model_parameters_classification, feature_vectors_classification
):

    classifier = TensorFlowMicro(config={})

    model_parameters_classification["threshold"] = 2
    classifier.load_model(model_parameters_classification)

    classifier.preprocess(1, feature_vectors_classification)

    results = classifier.recognize_vectors(
        package(feature_vectors_classification.values)
    )

    assert results["UnknownPercent"] == 100.0


def test_get_model_profile(model_parameters_classification):
    classifier = TensorFlowMicro(config={})

    tflite_model_buffer = binascii.unhexlify(
        model_parameters_classification["tflite"].encode("ascii")
    )
    model_profile = classifier.get_model_profile(tflite_model_buffer)
    tf_size = classifier.compute_tensor_arena_size(model_profile)

    assert tf_size == 2048


def test_load_model(model_parameters_classification):
    classifier = TensorFlowMicro(config={})

    assert classifier._model is None

    classifier.load_model(model_parameters_classification)

    assert classifier.model_parameters == model_parameters_classification
    assert classifier._model is not None


def test_get_input_output_details(model_parameters_classification):
    classifier = TensorFlowMicro(config={})
    params = classifier.get_input_output_details(model_parameters_classification)

    assert params["num_inputs"] == 26 and params["num_outputs"] == 1
    assert params["input_shape"] == [1, 26, 1]
    assert params["input_quantization"] == (1.0, 0)


@pytest.mark.django_db
def test_compute_cost(model_parameters_classification, loaddata):
    loaddata("test_classifier_costs")

    classifier = TensorFlowMicro(config={})
    classifier.load_model(model_parameters_classification)
    expected_total_flash_size = 2416
    expected_total_sram = 2176
    costs = classifier.compute_cost(model_parameters_classification)
    assert costs["flash"] == expected_total_flash_size
    assert costs["sram"] == expected_total_sram

    assert costs["cycle_count"] == 222574


def package(data):
    vector_list = []
    for index, _ in enumerate(data):
        item_ints = [i for i in data[index][:-1]]
        pkg_dict = {
            "Category": int((data[index][-1])),
            "CategoryVector": [],
            "DistanceVector": [],
            "Vector": list(item_ints),
        }
        vector_list.append(pkg_dict)

    return vector_list
