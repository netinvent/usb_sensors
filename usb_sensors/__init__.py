#! /usr/bin/env python3
#  -*- coding: utf-8 -*-


__intname__ = "usb_dogratian_sensors"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2022 Orsiris de Jong - NetInvent SASU"
__licence__ = "BSD 3 Clause"
__version__ = "1.0"
__build__ = "2022071501"


from typing import Dict, List
from logging import getLogger
import serial.tools.list_ports
import serial


USB_TNH_VID = "0x03EB"
USB_TNH_PID = "0x2310"
USB_PA_VID = "0xBADCAFE"  # TODO: Ask DogRatIan what VID:PID USB-PA has
USB_PA_PID = "0xBADCAFE"

SERIAL_SETTINGS = {
    "baudrate": 115200,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
}


logger = getLogger(__name__)


class USBSensor:
    def __init__(self, port=None, read_light=False):
        # type: (str, bool) -> None
        self._port = port
        self._read_light = read_light

    @staticmethod
    def find_sensors():
        # type: () -> Dict[str, List]
        _sensor_ports = {"USB-TnH": [], "USB-PA": []}
        for port in serial.tools.list_ports.comports():
            if port.vid == int(USB_TNH_VID, 16) and port.pid == int(USB_TNH_PID, 16):
                _sensor_ports["USB-TnH"].append(port.device)
            if port.vid == int(USB_PA_VID, 16) and port.pid == int(USB_PA_PID, 16):
                _sensor_ports["USB-PA"].append(port.device)
        return _sensor_ports

    @staticmethod
    def find_usb_tnh_sensors():
        return USBSensor.find_sensors()["USB-TnH"]

    @staticmethod
    def find_usb_pa_sensors():
        return USBSensor.find_sensors()["USB-PA"]

    def _read_data(self, command):
        # type: (str) -> str

        if self._read_light:
            self.led = True

        if command not in ["GI", "GV", "GT", "GH", "GP", "GN", "GSJON"]:
            raise ValueError('Invalid command requested: "{}"'.format(command))
        try:
            with serial.Serial(
                self._port,
                timeout=0.1,
                **SERIAL_SETTINGS
            ) as ser:
                ser.write("{}\r\n".format(command).encode("utf-8"))
                result = ser.read(size=64).decode("utf-8")
                result = result.strip("\r\n")
                if command in ["GT", "GH", "GP"]:
                    result = float(result)

                # Deactivate light directly here so we reuse current serial handle
                if self._read_light:
                    ser.write("{}={}\r\n".format('I', '0').encode("utf-8"))

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
            with serial.Serial(
                self._port,
                timeout=0.1,
                **SERIAL_SETTINGS
            ) as ser:
                ser.write("{}={}\r\n".format(command, value).encode("utf-8"))
                result = ser.read(size=64).decode("utf-8")
                if result == "OK\n":
                    return True
                logger.error("Command %s failed with result: %s" % (command, result))
                return False
        except serial.SerialException as exc:
            message = "Cannot execute write command %s: %s" % (command, exc)
            logger.error(message)
            # Unless we use the led switch, we'll complain
            if command != "I":
                raise OSError(message)

    @property
    def model(self):
        return self._read_data("GI")

    @property
    def version(self):
        return self._read_data("GV")

    @property
    def temperature(self):
        return self._read_data("GT")

    @property
    def humidity(self):
        return self._read_data("GH")

    @property
    def name(self):
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
        if isinstance(value, bool):
            self._write_data("I", "1" if value else "0")
        else:
            raise ValueError(
                "led can only be turned on or off... Do not try to alter reality neo."
            )

    @property
    def identification(self):
        return {
            "model": self.model,
            "version": self.version,
            "name": self.name
        }

    def __str__(self):
        return str(self.identification)
