# Dogratian USB-TnH and USB-PA python lib

This library makes usage of https://www.dogratian.com sensors easy

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
   'USB-TnH': ['COM1', 'COM2'],
   'USB-PA': ['COM3', 'COM4']
} 
```
You can also use `USBSensor.find_tnh_sensors()` or `USBSensor.find_pa_sensors()` which will directly return the list of serial ports.

# Writing data

As DogRatIan suggests, you can set Name sensor to a max 8 char string, and turn on/off led.
USBSensor class has write methods implemented as setter properties, eg:

```python
sensor = USBSensor('/dev/ttyUSB2')
sensor.name = 'MYSENSOR'
sensor.led = True
```

# Readed led
Optionally, we can enable the led indicator while reading with:
```python
sensor = USBSensor('COM4', read_light=True)
```