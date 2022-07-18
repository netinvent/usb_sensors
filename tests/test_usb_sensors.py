#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of usb_sensors module

__intname__ = "usb_dogratian_sensors_tests"
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2022 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__build__ = '2022071801'


from time import sleep
from usb_sensors import USBSensor


def test_usb_sensors():
    sensor_ports = USBSensor.find_sensors()
    if not sensor_ports:
        print("No sensors found")
    for sensor_port in sensor_ports:
        print("Found sensor at port {}".format(sensor_port))
        sensor = USBSensor(sensor_port, read_light=True)

        count = 0
        try:
            while count < 10:
                temperature = sensor.temperature
                humidity = sensor.humidity
                print("Current temperature: {} °C".format(temperature))
                print("Current humidity: {} %".format(humidity))
                assert isinstance(temperature, float), 'Temperature should be a float'
                assert isinstance(humidity, float), 'Humidity should be a float'
                sleep(.1)
                count += 1
        except PermissionError as exc:
            print("We don't have permission to use serial ports: {}".format(exc))


if __name__ == "__main__":
    test_usb_sensors()
