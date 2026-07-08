#aht20_module.py

import machine
import time
from ahtx0 import AHT20

_sensor = None
_temp = None
_hum = None
_last_read_ms = 0
_read_interval_ms = 2000

def init():
    global _sensor
    i2c = machine.I2C(1, freq=400000)

    print("I2C设备扫描:")
    devices = i2c.scan()
    if devices:
        for addr in devices:
            print("地址: 0x" + hex(addr)[2:])
    else:
        raise Exception("未找到I2C设备")

    _sensor = AHT20(i2c)
    print("AHT20初始化完成")

def task():
    global _temp, _hum, _last_read_ms

    now = time.ticks_ms()
    if time.ticks_diff(now, _last_read_ms) < _read_interval_ms:
        return

    _last_read_ms = now
    _temp = _sensor.temperature
    _hum = _sensor.relative_humidity

def get_data():
    return _temp, _hum