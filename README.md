# Dogratian USB-TnH and USB-PA python lib

This library makes usage of https://www.dogratian.com sensors easy

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/netinvent/usb_sensors.svg)](http://isitmaintained.com/project/netinvent/usb_sensors "Percentage of issues still open")
[![linux-tests](https://github.com/netinvent/usb_sensors/actions/workflows/linux.yaml/badge.svg)](https://github.com/netinvent/usb_sensors/actions/workflows/linux.yaml)
[![windows-tests](https://github.com/netinvent/usb_sensors/actions/workflows/windows.yaml/badge.svg)](https://github.com/netinvent/usb_sensors/actions/workflows/windows.yaml)
[![GitHub Release](https://img.shields.io/github/release/netinvent/usb_sensors.svg?label=Latest)](https://github.com/netinvent/usb_sensors/releases/latest)

Setup:
`pip install usb_sensors`  # Future if DogRatIan agrees 

Quick Usage:
```python
from usb_sensors import USBSensor

# Returns serial port names for every connected DogRatIan device
sensor_ports = USBSensor.find_tnh_sensors()  # or USBSensor.find_pa_sensors()

# Read data for every sensor on system
for sensor_port in sensor_ports:
    sensor = USBSensor(sensor_port)
    print(sensor.model)
    print(sensor.version)
    print(sensor.temperature)
    print(sensor.humidity)
    print(sensor.name)
```

DogRatIan uses USB-TnH (temperature and humidity sensors) as well as USB-PA (temperature, humidity and atmospheric pressure sensors).
Using `USBSensor.find_sensors()` will return a dictionary structure like:
```python
{ 
   'USB-TnH': ['COM1', 'COM2'],  # or /dev/ttyACM0 alike ports on Linux
   'USB-PA': ['COM3', 'COM4']
} 
```

The dictionnary can be used like
```python
from time import sleep
from usb_sensors import USBSensor

sensor_dict = USBSensor.find_sensors()
for sensor_type, sensor_ports in sensor_dict.items():
    for sensor_port in sensor_ports:
        print("Found sensor type {} at port {}".format(sensor_type, sensor_port))
        sensor = USBSensor(sensor_port, read_light=True)

        count = 0
        while count < 10:
            print("Current temperature: {}".format(sensor.temperature))
            print("Current humidity: {}".format(sensor.humidity))
            sleep(.1)
            count += 1

```
You can also use `USBSensor.find_tnh_sensors()` or `USBSensor.find_pa_sensors()` which will directly return the list of serial ports for each sensor type.

# Writing data

As DogRatIan suggests, you can set Name sensor to a max 8 char string, and turn on/off led.
USBSensor class has write methods implemented as setter properties, eg:

```python
from usb_sensors import USBSensor

sensor = USBSensor('/dev/ttyUSB2')
sensor.name = 'MYSENSOR'
sensor.led = True
# Some code
sensor.led = False
```

# Readed led
Optionally, we can enable the led indicator while reading with:
```python
from usb_sensors import USBSensor

sensor = USBSensor('COM4', read_light=True)
print(sensor.name)  # Light flashes while reading value
```

# Error handling

USBSensor class will raise two types of exceptions:
- ValueError when invalid opcode is given to sensor
- OSError when serial communication fails (most time you need to be root/administrator to have permissions over serial ports)