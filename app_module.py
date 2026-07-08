# app_module.py

import time
import aht20_module
import tcp_module
import crash_module
import gnss_module

_last_send_ms = 0
_send_interval_ms = 2000   # 2秒上传一次


def init():
    global _last_send_ms
    _last_send_ms = 0


def task():
    global _last_send_ms

    if not tcp_module.is_connected():
        return

    now = time.ticks_ms()
    if time.ticks_diff(now, _last_send_ms) < _send_interval_ms:
        return

    _last_send_ms = now

    temp, hum = aht20_module.get_data()
    acc_x, acc_y, acc_z, acc_total = crash_module.get_data()
    crash_flag, crash_count, peak_acc = crash_module.get_crash()
    lat, lon, has_fix = gnss_module.get_data()

    if temp is None or hum is None:
        return

    lat_str = "%.6f" % lat if (has_fix and lat is not None) else "--"
    lon_str = "%.6f" % lon if (has_fix and lon is not None) else "--"

    msg = "temp=%.1f,hum=%.1f,acc=%.2f,crash=%d,count=%d,peak=%.2f,gps=%d,lat=%s,lon=%s" % (
        temp,
        hum,
        acc_total,
        1 if crash_flag else 0,
        crash_count,
        peak_acc,
        1 if has_fix else 0,
        lat_str,
        lon_str
    )

    ok = tcp_module.send_line(msg)

    if ok:
        print("发送数据:", msg)

        # 发送成功后清除本次碰撞标志，但碰撞次数会保留；LCD会靠碰撞次数保持GPS页面
        if crash_flag:
            crash_module.clear_crash()
