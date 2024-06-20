import json
import sys
from argparse import ArgumentParser
import time
import os
import serial
from colorama import init as color_init
from colorama import Fore, Style


class NoConnectionsSpecifiedException(Exception):
    pass


class NoCaptureSourcesException(Exception):
    pass


class InvalidDeviceConfigException(Exception):
    pass


def print_error(x):

    print(f"{Fore.RED}ERROR - {x}{Style.RESET_ALL}")


def print_pass(x):

    print(f"{Fore.GREEN}PASS - {x}{Style.RESET_ALL}")


def print_info(x):

    print(f"{Fore.CYAN}INFO - {x}{Style.RESET_ALL}")


class SerialReader:
    name = "SERIAL"

    def __init__(self, config, device_id, **kwargs):
        self._port = device_id
        self._baud_rate = config["baud_rate"]

    @property
    def port(self):
        return self._port

    @property
    def baud_rate(self):
        return self._baud_rate

    @staticmethod
    def _validate_config(config):

        if not isinstance(config, dict):
            raise InvalidDeviceConfigException("Invalid Configuration")

        if config.get("column_location", None) is None:
            raise InvalidDeviceConfigException(
                "Invalid Configuration: no column_location"
            )
        if config.get("sample_rate", None) is None:
            raise InvalidDeviceConfigException("Invalid Configuration: no sample_rate")

        if config.get("samples_per_packet", None) is None:
            raise InvalidDeviceConfigException(
                "Invalid Configuration: no samples_per_packet"
            )

        print_info("Found configuration:")
        print_info(config)

        return config

    def _write(self, command):
        with serial.Serial(self.port, self.baud_rate, timeout=1) as ser:
            ser.write(str.encode(command))

    def _read_line(self, flush_buffer=False):
        with serial.Serial(self.port, self.baud_rate, timeout=1) as ser:

            value = ser.readline()
            if flush_buffer:
                value = ser.readline()
            try:
                return value.decode("ascii")
            except:
                return None

    def _flush_buffer(self):
        with serial.Serial(self.port, self.baud_rate, timeout=1) as ser:
            return ser.reset_input_buffer()


class SerialStreamReader(SerialReader):
    def send_subscribe(self):
        self._write("connect")

    def send_unsubscribe(self):
        self._write("disconnect")

    def read_device_config(self, disconnect=True):

        config = None

        try:
            config = json.loads(self._read_line())
        except:
            if disconnect:
                self._write("disconnect")
                time.sleep(1.0)
                config = json.loads(self._read_line(flush_buffer=True))
            else:
                config = None

        if config is None:
            return None

        if self._validate_config(config):
            return config
        else:
            return None


def parse_ssf_file(path):
    config = dict()
    ssf_data = dict()
    try:
        with open(os.path.abspath(path), "r") as ssf:
            ssf_data = json.load(ssf)
    except json.decoder.JSONDecodeError:
        print_error("Couldn't parse SSF file. Make sure it is valid JSON")
        return None

    connections = ssf_data.get("device_connections", None)

    if connections is None:
        raise NoConnectionsSpecifiedException(
            "A device Connection must be specified in the SSF file!"
        )

    for conn in connections:
        sp = conn.get("serial_port_configuration", None)
        if sp is None:
            continue
        config["baud_rate"] = sp["baud"]
        config["max_live_sample_rate"] = sp["max_live_sample_rate"]

    capture_sources = ssf_data.get("capture_sources", None)
    if capture_sources is None:
        raise NoCaptureSourcesException("Capture Sources need to be included!")
    config["available_sensors"] = list()
    config["acceptable_sample_rates"] = list()
    for source in capture_sources:
        config["acceptable_sample_rates"].extend(source["sample_rates"])
        for sensor in source["sensors"]:
            if sensor["type"] not in config["available_sensors"]:
                config["available_sensors"].append(sensor["type"])

    return config


def validate_device_config_works_with_ssf(ssf_data, device_config):
    fail = False
    if device_config["sample_rate"] not in ssf_data["acceptable_sample_rates"]:
        print_error("Device config did not contain a sample rate from the SSF file!")
        return False
    elif device_config["sample_rate"] > ssf_data["max_live_sample_rate"]:
        sr = device_config["sample_rate"]
        max = ssf_data["max_live_sample_rate"]
        print_error(f"Sample rate {sr} exceeds max of {max}!")
        return False
    else:
        print_pass("Sample Rate OK")
    for col, col_i in device_config["column_location"].items():
        if col[-1].lower() in ["x", "y", "z"]:
            if col[:-1] in ssf_data["available_sensors"]:
                print_pass(f"{col} OK")
            else:
                print_error(f"{col} Not Within available sensors!")
                print_error(ssf_data["available_sensors"])
                fail = True
    if fail:
        return False
    return True


def check_connect_disconnect(serial_port, device_config):
    print_info("Checking Connection...  ")
    serial_port._flush_buffer()
    serial_port.send_subscribe()
    time.sleep(1)
    serial_port._flush_buffer()

    try:
        test1 = serial_port.read_device_config(disconnect=False)
        if test1 is not None:
            print_error("Connect not received by device!")
            return False
    except:
        pass
    print_pass("Connect received by device")
    serial_port.send_unsubscribe()
    time.sleep(1)
    serial_port._flush_buffer()
    conf = serial_port.read_device_config(disconnect=False)
    if conf == device_config:
        print_pass("Disconnect received and config info being sent")
    return True


def main(argv):
    parser = ArgumentParser()

    # Adding optional argument
    parser.add_argument(
        "-f",
        "--ssf_file",
        dest="ssf_file",
        required=True,
        help="Path to SSF File used to import your device into the Data Studio",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        required=True,
        help="COM port used by device to communicate with the Data Studio",
    )
    # Read arguments from command line
    args = parser.parse_args()
    ssf_data = parse_ssf_file(f"{args.ssf_file}")
    if ssf_data is None:
        return
    print_info(ssf_data)
    serial_conn = SerialStreamReader(ssf_data, args.port)
    serial_conn._flush_buffer()
    device_config = serial_conn.read_device_config()
    if device_config is None:
        print_error("Device configuration not being sent")
        return
    config_ok = validate_device_config_works_with_ssf(ssf_data, device_config)

    if config_ok:
        if check_connect_disconnect(serial_conn, device_config):
            print_pass("All Checks Passed")
        else:
            print_error("Connect/disconnect check did not pass")


if __name__ == "__main__":
    color_init()
    main(sys.argv[1:])
