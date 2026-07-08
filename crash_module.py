# crash_module.py

import machine
import time
import math
from lis2dh12 import LIS2DH12

_sensor = None

_crash_flag = False
_crash_count = 0

_acc_x = 0
_acc_y = 0
_acc_z = 0
_acc_total = 0

_peak_acc = 0

_last_read_ms = 0
_read_interval_ms = 20       # 20ms检测一次

_last_crash_ms = 0
_crash_cooldown_ms = 3000    # 3秒内只算一次碰撞

CRASH_THRESHOLD = 35.0       # 碰撞阈值，单位 m/s²


def init():
    global _sensor
    i2c = machine.I2C(1, freq=400000)

    print("LIS2DH12 I2C设备扫描:")
    devices = i2c.scan()
    if devices:
        for addr in devices:
            print("地址: 0x" + hex(addr)[2:])
    else:
        raise Exception("未找到I2C设备")

    _sensor = LIS2DH12(i2c)
    print("LIS2DH12初始化完成")


def task():
    global _acc_x, _acc_y, _acc_z, _acc_total
    global _peak_acc, _crash_flag, _crash_count
    global _last_read_ms, _last_crash_ms

    if _sensor is None:
        return

    now = time.ticks_ms()

    if time.ticks_diff(now, _last_read_ms) < _read_interval_ms:
        return

    _last_read_ms = now

    try:
        x, y, z = _sensor.acceleration

        _acc_x = x
        _acc_y = y
        _acc_z = z

        total = math.sqrt(x * x + y * y + z * z)
        _acc_total = total

        # 只要当前有待上传碰撞事件，就持续记录本次事件峰值
        if _crash_flag:
            if total > _peak_acc:
                _peak_acc = total

        # 检测新碰撞
        if total >= CRASH_THRESHOLD:
            if time.ticks_diff(now, _last_crash_ms) > _crash_cooldown_ms:
                _crash_flag = True
                _crash_count += 1
                _last_crash_ms = now

                # 新碰撞开始时，peak 直接记录当前值
                _peak_acc = total

                print("检测到碰撞!")
                print("当前碰撞加速度: %.2f m/s²" % total)

    except Exception as e:
        print("LIS2DH12读取失败:", e)


def get_data():
    return _acc_x, _acc_y, _acc_z, _acc_total


def get_crash():
    return _crash_flag, _crash_count, _peak_acc


def clear_crash():
    global _crash_flag, _peak_acc
    _crash_flag = False
    _peak_acc = 0