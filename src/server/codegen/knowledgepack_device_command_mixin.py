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

import logging

from codegen.utils import c_line_nr

logger = logging.getLogger(__name__)


class DeviceCommandGenerationError(Exception):
    pass


class DeviceCommandMixin(object):
    """
    The sensor config mixin is responsible for taking project/capture
    configuration and turning it into C code for the Device Command
    structures
    """

    def create_device_command_structure_def(self):
        output = [
            "const struct sensor_config_msg recognition_config[] = {",
            c_line_nr(1, "SENSOR_CONFIG_CLEAR_MSG(),"),
        ]

        return output

    def create_device_command_structure_end(self):
        output = [c_line_nr(1, "SENSOR_CONFIG_DONE_MSG()"), "};"]
        return output

    def create_device_command_from_source_selection(self, source_name):
        """
        We will use defaults for some of the values for setting device config.
        """
        sample_rate = self.device_config.get("sample_rate", -1)
        output = []
        if source_name == "motion":
            tmp_params = [{"name": "Sensor Range", "value": 2}]
            output.append(
                c_line_nr(
                    1,
                    device_command_create_motion_source(
                        "accel", sample_rate, tmp_params
                    ),
                )
            )
            tmp_params = [{"name": "Sensor Range", "value": 0}]
            output.append(
                c_line_nr(
                    1,
                    device_command_create_motion_source(
                        "gyro", sample_rate, tmp_params
                    ),
                )
            )
        elif source_name == "audio":
            output.append(c_line_nr(1, device_command_create_audio_source(sample_rate)))
        elif source_name == "custom":
            # Do nothing here because we don't know what to do. User will have to specify.
            output.append("")

        return output

    def create_device_command_from_capture_config(self, kb_model):
        """
        Pull capture config form device_config['source'] UUID, uses that
        to populate items for DeviceCommand-based recognition
        """
        output = []
        source_uuid = kb_model["sensor_plugin"]
        capture_config = kb_model["capture_configuration"]
        if not capture_config:
            raise DeviceCommandGenerationError(
                "Capture Configuration with {} not found".format(source_uuid)
            )

        capture_sources = capture_config.configuration.get("capture_sources", None)

        if capture_sources is None:
            raise DeviceCommandGenerationError(
                "A capture configuration must be provided."
            )

        if type(capture_sources) is list:
            for source in capture_sources:
                source_base_name = source.get("name", None)
                rate = source.get("sample_rate", 104)
                if "motion" in source_base_name.lower():
                    for sensor in source.get("sensors"):
                        output.append(
                            c_line_nr(
                                1,
                                device_command_create_motion_source(
                                    sensor.get("type"),
                                    rate,
                                    sensor.get("parameters", []),
                                ),
                            )
                        )
                if "mayhew" in source_base_name.lower():
                    output.append(
                        c_line_nr(
                            1,
                            device_command_create_mayhew_source(
                                rate, source.get("sensors", None)
                            ),
                        )
                    )
                if "ad7476" in source_base_name.lower():
                    output.append(
                        c_line_nr(
                            1,
                            device_command_create_ad7476_source(
                                rate, source.get("sensors", None)
                            ),
                        )
                    )
                if "audio" in source_base_name.lower():
                    output.append(
                        c_line_nr(1, device_command_create_audio_source(rate))
                    )

        return output


def sensor_macro_from_plugin_name(name):
    if "motion" in name.lower():
        return "SENSOR_MOTION"
    if "mayhew" in name.lower():
        return "SENSOR_ADC_LTC_1859_MAYHEW"
    if "audio" in name.lower():
        return "SENSOR_AUDIO"
    if "ad7476" in name.lower():
        return "SENSOR_ADC_AD7476"

    return "SENSOR_CUSTOM"


def device_command_create_motion_source(name, sample_rate, source_params):
    out = ""
    sensor_id = ""
    if type(source_params) is list:

        for param in source_params:
            if param.get("name", None) != "Sensor Range":
                continue
            param_val = param.get("value")

            if int(param_val) % 10 != 0:
                # Non-Multiplied values are 2,4,6,8,16
                param_val = hex(int(param_val) * 10)

            if "accel" in name.lower():
                sensor_id = "SENSOR_ENG_VALUE_ACCEL"
            if "gyro" in name.lower():
                param_val = 0  # 2000 dps for gyro.
                sensor_id = "SENSOR_ENG_VALUE_GYRO"
            if "mag" in name.lower():
                sensor_id = "SENSOR_ENG_VALUE_MAG"
            out = "SENSOR_CONFIG_IMU_MSG("
            out = out + "{},{},{}),".format(sensor_id, sample_rate, param_val)

    return out


def device_command_create_mayhew_source(sample_rate, channels):
    out = ""
    sensor_id = "SENSOR_ADC_LTC_1859_MAYHEW"
    channel_values = [hex(255), hex(255), hex(255), hex(255)]
    index = 0
    if channels is None:
        return out
    for channel in channels:
        try:
            index = int(channel.get("type", "Channel 1")[-2:]) - 1
            channel_values[index] = hex(channel["parameters"][0].get("value", 255))
        except KeyError:
            return ""
        except IndexError:
            return ""
    out = "SENSOR_CONFIG_ADC_MSG("
    out = out + "{},{},SENSOR_CONFIG_ARRAY({})),".format(
        sensor_id, sample_rate, ",".join(channel_values)
    )

    return out


def device_command_create_ad7476_source(sample_rate, channels):
    out = ""
    sensor_id = "SENSOR_ADC_AD7476"
    channel_values = []
    if channels is None:
        return out
    # AD7476 is ONE channel ADC. Digilent AD1 has 2 chips.
    # Only use one channel here.
    channel = channels[0]
    for param in channel["parameters"]:
        channel_values.append(str(param.get("value", 0)))
    out = "SENSOR_CONFIG_AD7476_MSG("
    out = out + "{},{},{}),".format(sensor_id, sample_rate, ",".join(channel_values))

    return out


def device_command_create_audio_source(sample_rate, mic_config_arr=None):
    out = ""
    sensor_id = "SENSOR_AUDIO"
    # Just use platform default for now. This would be stored later.
    mic_cfg = ["0x01", "0x00", "0x00", "0x00", "0x00", "0x00", "0x00", "0x00"]
    out = "SENSOR_CONFIG_AUDIO_MSG("
    out = out + "{},{}, 16, SENSOR_CONFIG_ARRAY({})),".format(
        sensor_id, sample_rate, ",".join(mic_cfg)
    )

    return out
