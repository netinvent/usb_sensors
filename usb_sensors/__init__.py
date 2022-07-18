#! /usr/bin/env python3
#  -*- coding: utf-8 -*-


__intname__ = "usb_dogratian_sensors"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2022 Orsiris de Jong - NetInvent SASU"
__licence__ = "BSD 3 Clause"
__version__ = "1.0"
__build__ = "2022071801"


from typing import Optional, List
from logging import getLogger
import serial.tools.list_ports
import serial
import json
from contextlib import contextmanager
from threading import Lock


LOCK = None

# DogRatIan USB sensor ID
USB_VID = "0x03EB"
USB_PID = "0x2310"


SERIAL_SETTINGS = {
    "baudrate": 115200,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
}


logger = getLogger(__name__)


@contextmanager
def _with_Lock():
    # This is a singleton, pylint: disable=global-statement
    global LOCK

    if LOCK is None:
        LOCK = Lock()

    LOCK.acquire()
    yield
    if LOCK is not None:
        LOCK.release()


class USBSensor:
    def __init__(self, port=None, read_light=False):
        # type: (str, bool) -> None
        self._port = port
        self._read_light = read_light
        self._location = (
            None  # For easier identification purposes (eg 'mainframe room')
        )

    @property
    def location(self):
        # type:  () -> str
        return self._location

    @location.setter
    def location(self, value):
        # type:  (str) -> None
        self._location = value

    @staticmethod
    def find_sensors():
        # type: () -> List[str]
        _sensor_ports = []
        for port in serial.tools.list_ports.comports():
            if port.vid == int(USB_VID, 16) and port.pid == int(USB_PID, 16):
                _sensor_ports.append(port.device)
        return _sensor_ports

    def _read_data(self, command):
        # type: (str) -> Optional[str]

        if self._read_light:
            self.led = True

        if command not in ["GI", "GV", "GT", "GH", "GP", "GN", "GJSON"]:
            raise ValueError('Invalid command requested: "{}"'.format(command))
        try:
            with _with_Lock():
                with serial.Serial(self._port, timeout=0.1, **SERIAL_SETTINGS) as ser:
                    ser.write("{}\r\n".format(command).encode("utf-8"))
                    result = ser.read(size=64).decode("utf-8")
                    if len(result) == 0:
                        result = None
                    else:
                        result = result.strip("\r\n")
                    # Deactivate light directly here so we reuse current serial handle
                    if self._read_light:
                        ser.write("{}={}\r\n".format("I", "0").encode("utf-8"))
                    return result
        except serial.SerialException as exc:

            error_message = "Cannot execute read command %s: %s" % (command, exc)
            logger.error(error_message)
            if self._read_light:
                self.led = False
            raise OSError(error_message)

    def _write_data(self, command, value):
        # type: (str, str) -> bool
        if command not in ["N", "I"]:
            raise ValueError('Invalid command requested: "{}"'.format(command))
        try:
            with _with_Lock():
                with serial.Serial(self._port, timeout=0.1, **SERIAL_SETTINGS) as ser:
                    ser.write("{}={}\r\n".format(command, value).encode("utf-8"))
                    result = ser.read(size=64).decode("utf-8")
                    if result == "OK\n":
                        return True
                    logger.error(
                        "Command %s failed with result: %s" % (command, result)
                    )
                    return False
        except serial.SerialException as exc:
            message = "Cannot execute write command %s: %s" % (command, exc)
            logger.error(message)
            # Unless we use the led switch, we'll complain
            if command != "I":
                raise OSError(message)

    @property
    def model(self):
        # type:  () -> str
        return self._read_data("GI")

    @property
    def version(self):
        # type:  () -> str
        return self._read_data("GV")

    @property
    def temperature(self):
        # type:  () -> float
        data = self._read_data("GT")
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def humidity(self):
        # type:  () -> float
        data = float(self._read_data("GH"))
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def pressure(self):
        # type:  () -> float
        data = float(self._read_data("GP"))
        try:
            return float(data)
        except TypeError:
            return data

    @property
    def all(self):
        # type:  () -> dict
        data = json.loads(self._read_data("GJSON"))
        json_output = {}
        for data_name in ["temperature", "humidity", "pressure"]:
            data_original_name = data_name[0:1].upper()
            try:
                json_output[data_name] = float(data[data_original_name])
            except TypeError:
                json_output[data_name] = data[data_original_name]
            except KeyError:
                pass
        return json_output

    @property
    def name(self):
        # type:  () -> str
        return self._read_data("GN")

    @name.setter
    def name(self, value):
        if isinstance(value, str) and 0 < len(value) <= 8:
            self._write_data("N", value)
        else:
            raise ValueError("Name cannot be longer than 8 characters")

    @property
    def led(self):
        raise ValueError("Light status is not available. Please use your eyes.")

    @led.setter
    def led(self, value):
        # type:  (bool) -> None
        if isinstance(value, bool):
            self._write_data("I", "1" if value else "0")
        else:
            raise ValueError(
                "led can only be turned on or off... Do not try to alter reality neo."
            )

    @property
    def identification(self):
        # type:  () -> dict
        return {"model": self.model, "version": self.version, "name": self.name}

    def __str__(self):
        return str(self.identification)
