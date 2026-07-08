# main.py

import time
import aht20_module
import tcp_module
import app_module
import crash_module
import lcd_module
import gnss_module

_gnss_ok = False


def all_init():
    global _gnss_ok
    print("系统初始化开始")

    # 先初始化 LCD：开机显示 Quectel 图像 5 秒
    lcd_module.init()

    aht20_module.init()
    crash_module.init()

    try:
        gnss_module.init()
        _gnss_ok = True
    except Exception as e:
        _gnss_ok = False
        print("GNSS初始化失败，继续运行其他功能:", e)

    tcp_module.init()
    app_module.init()

    print("系统初始化完成")


def main():
    all_init()

    try:
        while True:
            tcp_module.task()       # TCP连接维护
            aht20_module.task()     # 温湿度采集
            crash_module.task()     # 碰撞检测

            if _gnss_ok:
                gnss_module.task()  # GNSS定位更新

            app_module.task()       # 数据上传
            lcd_module.task()       # LCD显示

            time.sleep_ms(20)

    except KeyboardInterrupt:
        print("程序停止")

    finally:
        try:
            tcp_module.close()
        except:
            pass

        try:
            if _gnss_ok:
                gnss_module.close()
        except:
            pass

        print("资源已释放")


main()
