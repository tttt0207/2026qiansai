#gnss_module.py

import quectel
import time

_gnss = None
_latitude = None
_longitude = None
_has_fix = False
_last_read_ms = 0
_read_interval_ms = 1000   # 1秒读一次

def init():
    global _gnss
    _gnss = quectel.GNSS()

    if not _gnss.start():
        raise Exception("GNSS启动失败!")

    print("GNSS初始化完成")

def task():
    global _latitude, _longitude, _has_fix, _last_read_ms

    now = time.ticks_ms()
    if time.ticks_diff(now, _last_read_ms) < _read_interval_ms:
        return

    _last_read_ms = now

    try:
        loc = _gnss.get_location()
        if loc:
            _latitude = loc['latitude']
            _longitude = loc['longitude']
            _has_fix = True
            print("GNSS: 纬度=%.6f, 经度=%.6f" % (_latitude, _longitude))
        else:
            _has_fix = False
            print("GNSS: 定位中...")
    except Exception as e:
        _has_fix = False
        print("GNSS错误:", e)

def has_fix():
    return _has_fix

def get_data():
    return _latitude, _longitude, _has_fix

def close():
    global _gnss
    try:
        if _gnss:
            _gnss.stop()
            print("GNSS已停止")
    except Exception as e:
        print("GNSS停止异常:", e)