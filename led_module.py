#led_module.py

import machine
import time

_led = None
_last_toggle_ms = 0
_led_state = 0

def init():
    global _led
    _led = machine.Pin('LED_RED', machine.Pin.OUT)

def task():
    global _last_toggle_ms, _led_state

    now = time.ticks_ms()
    if time.ticks_diff(now, _last_toggle_ms) >= 500:
        _last_toggle_ms = now
        _led_state = 0 if _led_state else 1
        _led.value(_led_state)