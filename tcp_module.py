#tcp_module.py

import usocket as socket
import time
import config

_client = None
_connected = False
_last_retry_ms = 0
_retry_interval_ms = 5000   # 重连间隔，先设 5 秒
_connecting = False

def safe_close():
    global _client, _connected, _connecting

    s = _client
    _client = None
    _connected = False
    _connecting = False

    try:
        if s is not None:
            s.close()
    except KeyboardInterrupt:
        print("关闭TCP时被中断，忽略")
    except Exception as e:
        print("关闭TCP异常，忽略:", e)

def init():
    global _last_retry_ms
    safe_close()
    _last_retry_ms = time.ticks_ms()

def connect():
    global _client, _connected, _connecting

    # 已连接就不重复连
    if _connected:
        return True

    # 防止重复进入
    if _connecting:
        return False

    _connecting = True
    s = None

    try:
        print("开始连接TCP服务器...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((config.SERVER_IP, config.SERVER_PORT))

        _client = s
        _connected = True
        _connecting = False
        print("TCP连接成功")
        return True

    except Exception as e:
        print("TCP连接失败:", e)

        # 关键：失败时一定释放这次新建的 socket
        try:
            if s is not None:
                s.close()
        except:
            pass

        _client = None
        _connected = False
        _connecting = False
        return False

def task():
    global _last_retry_ms

    if _connected:
        return

    now = time.ticks_ms()
    if time.ticks_diff(now, _last_retry_ms) >= _retry_interval_ms:
        _last_retry_ms = now
        connect()

def send_line(text):
    global _connected

    if not _connected or _client is None:
        return False

    try:
        _client.send((text + "\r\n").encode())
        return True

    except Exception as e:
        print("TCP发送失败:", e)

        # 关键：发送失败后也要立刻关闭，等下次 task() 重连
        safe_close()
        return False

def is_connected():
    return _connected

def close():
    safe_close()