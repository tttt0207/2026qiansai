# Smart Helmet Embedded System

本项目为嵌入式智能头盔演示系统，基于 Quectel EC200U-CN 开发板实现。

## 功能

- LCD 开机 Logo 显示
- 温湿度数据采集
- 加速度 / 碰撞检测
- 碰撞后切换 GPS 经纬度显示界面
- TCP 数据上传
- GNSS 定位信息获取

## 文件说明

- `main.py`：主程序入口
- `lcd_module.py`：LCD 显示模块
- `aht20_module.py`：温湿度采集模块
- `crash_module.py`：碰撞检测模块
- `gnss_module.py`：GNSS 定位模块
- `tcp_module.py`：TCP 通信模块
- `app_module.py`：数据整合与上传模块
- `images1.py`：LCD Logo 图片数据

## 运行方式

将所有 `.py` 文件上传到开发板根目录，确保主程序文件名为 `main.py`，上电后自动运行。
