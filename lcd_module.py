# lcd_module.py
# 开机显示 Quectel Logo 5s；正常显示数据界面；发生碰撞后切换到 GPS 经纬度界面一段时间

import machine
import time
from st7735 import LCD
from images1 import Quectel_Icon_160x20
import aht20_module
import crash_module
import tcp_module
import gnss_module

_lcd = None
_last_show_ms = 0
_show_interval_ms = 1000     # 1秒刷新一次

PAGE_DATA = 0
PAGE_GPS = 1
_page = PAGE_DATA
_gps_page_keep_ms = 15000    # 碰撞后 GPS 界面保持 15 秒
_gps_page_until_ms = 0
_last_crash_count_seen = 0

_last_temp_str = ""
_last_hum_str = ""
_last_acc_str = ""
_last_crash_str = ""
_last_peak_str = ""
_last_tcp_str = ""

_last_gps_state_str = ""
_last_lat_str = ""
_last_lon_str = ""
_last_count_str = ""


def init():
    global _lcd
    spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0)
    _lcd = LCD(spi, dc_pin="F12", cs_pin="D14")
    _lcd.set_rotation(1)

    show_boot_logo()
    time.sleep(5)
    show_data_frame()
    print("LCD初始化完成")


def show_boot_logo():
    if _lcd is None:
        return
    _lcd.fill_screen(_lcd.BLACK)
    # 160x20 的 Quectel 图像，放在屏幕中间附近
    _lcd.show_image(0, 54, 160, 20, Quectel_Icon_160x20)
    _lcd.flush()
    print("显示Quectel开机图像")


def show_data_frame():
    global _page
    global _last_temp_str, _last_hum_str, _last_acc_str, _last_crash_str, _last_peak_str, _last_tcp_str
    _page = PAGE_DATA
    _last_temp_str = ""
    _last_hum_str = ""
    _last_acc_str = ""
    _last_crash_str = ""
    _last_peak_str = ""
    _last_tcp_str = ""

    _lcd.fill_screen(_lcd.BLACK)
    _lcd.show_string(0, 0, "Sensor & Crash", _lcd.BLUE, _lcd.BLACK, 16)
    _lcd.show_string(0, 22, "Temp:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 42, "Humi:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 62, "Acc:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 82, "Crash:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 102, "TCP:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.flush()


def show_gps_frame():
    global _page
    global _last_gps_state_str, _last_lat_str, _last_lon_str, _last_count_str, _last_peak_str
    _page = PAGE_GPS
    _last_gps_state_str = ""
    _last_lat_str = ""
    _last_lon_str = ""
    _last_count_str = ""
    _last_peak_str = ""

    _lcd.fill_screen(_lcd.BLACK)
    _lcd.show_string(0, 0, "Crash Detected", _lcd.RED, _lcd.BLACK, 16)
    _lcd.show_string(0, 22, "GPS:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 42, "Lat:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 62, "Lon:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 82, "Cnt:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(0, 102, "Peak:", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.flush()


def _update_line(x, y, old_text, new_text):
    if old_text == new_text:
        return old_text
    _lcd.show_string(x, y, "              ", _lcd.WHITE, _lcd.BLACK, 16)
    _lcd.show_string(x, y, new_text, _lcd.WHITE, _lcd.BLACK, 16)
    return new_text


def _show_data_page(temp, hum, acc_total, crash_flag, crash_count, peak_acc):
    global _last_temp_str, _last_hum_str, _last_acc_str, _last_crash_str, _last_peak_str, _last_tcp_str

    if temp is None or hum is None:
        temp_str = "--.-C"
        hum_str = "--.-%"
    else:
        temp_str = "%.1fC" % temp
        hum_str = "%.1f%%" % hum

    acc_str = "%.1f" % acc_total
    crash_str = ("YES %d" % crash_count) if crash_flag else ("NO  %d" % crash_count)
    tcp_str = "OK" if tcp_module.is_connected() else "NO"

    _last_temp_str = _update_line(65, 22, _last_temp_str, temp_str)
    _last_hum_str = _update_line(65, 42, _last_hum_str, hum_str)
    _last_acc_str = _update_line(65, 62, _last_acc_str, acc_str)
    _last_crash_str = _update_line(65, 82, _last_crash_str, crash_str)
    _last_tcp_str = _update_line(65, 102, _last_tcp_str, tcp_str)


def _show_gps_page(crash_count, peak_acc):
    global _last_gps_state_str, _last_lat_str, _last_lon_str, _last_count_str, _last_peak_str

    lat, lon, has_fix = gnss_module.get_data()
    gps_state_str = "FIX" if has_fix else "SEARCH"

    if has_fix and lat is not None and lon is not None:
        lat_str = "%.6f" % lat
        lon_str = "%.6f" % lon
    else:
        lat_str = "--"
        lon_str = "--"

    count_str = "%d" % crash_count
    peak_str = "%.1f" % peak_acc

    _last_gps_state_str = _update_line(55, 22, _last_gps_state_str, gps_state_str)
    _last_lat_str = _update_line(45, 42, _last_lat_str, lat_str)
    _last_lon_str = _update_line(45, 62, _last_lon_str, lon_str)
    _last_count_str = _update_line(45, 82, _last_count_str, count_str)
    _last_peak_str = _update_line(55, 102, _last_peak_str, peak_str)


def task():
    global _last_show_ms, _page, _gps_page_until_ms, _last_crash_count_seen

    if _lcd is None:
        return

    now = time.ticks_ms()
    if time.ticks_diff(now, _last_show_ms) < _show_interval_ms:
        return
    _last_show_ms = now

    temp, hum = aht20_module.get_data()
    acc_x, acc_y, acc_z, acc_total = crash_module.get_data()
    crash_flag, crash_count, peak_acc = crash_module.get_crash()

    # 只要碰撞次数增加，就切到 GPS 页面
    if crash_count > _last_crash_count_seen:
        _last_crash_count_seen = crash_count
        _gps_page_until_ms = time.ticks_add(now, _gps_page_keep_ms)
        show_gps_frame()

    # GPS 页面显示到时间后，自动返回正常数据页面
    if _page == PAGE_GPS and time.ticks_diff(_gps_page_until_ms, now) <= 0:
        show_data_frame()

    if _page == PAGE_GPS:
        _show_gps_page(crash_count, peak_acc)
    else:
        _show_data_page(temp, hum, acc_total, crash_flag, crash_count, peak_acc)

    _lcd.flush()
