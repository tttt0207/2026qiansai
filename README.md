# 2026qiansai - 智能骑行头盔终端

本项目基于 UniKnect Kit GEN-1 Pro / Quectel EC200U-CN 开发套件，设计并实现了一款面向骑行安全场景的智能骑行头盔终端。系统集成温湿度采集、加速度碰撞检测、GNSS 定位、TCP 数据上传、LCD 显示和 LED 状态提示等功能，可用于骑行状态监测、事故检测和应急定位展示。

设备上电后，LCD 首先显示 Quectel 启动画面，延时约 5 秒后进入实时监测界面。正常状态下，系统持续显示温湿度、加速度、碰撞状态和 TCP 连接状态；当检测到碰撞事件后，LCD 会自动切换到碰撞定位界面，显示当前 GNSS 定位状态、经纬度、碰撞次数和加速度峰值，并通过 TCP 上传相关数据。

---

## 一、项目功能

### 1. 开机启动显示

- 系统上电后自动运行 `main.py`
- LCD 显示 Quectel 启动画面
- 启动画面保持约 5 秒
- 随后自动进入实时数据监测界面

### 2. 温湿度采集

- 通过 AHT20 传感器采集环境温度和湿度
- 采集周期约为 2 秒
- 数据用于 LCD 显示和 TCP 上传

### 3. 碰撞检测

- 通过 LIS2DH12 加速度传感器采集三轴加速度
- 计算合加速度大小
- 当加速度超过设定阈值时判定为碰撞
- 记录碰撞次数和碰撞峰值
- 设有冷却时间，避免短时间内重复误触发

### 4. 碰撞后定位显示

- 正常状态下显示实时传感器数据
- 一旦检测到碰撞，LCD 自动切换至碰撞定位界面
- 定位界面显示 GNSS 状态、纬度、经度、碰撞次数和加速度峰值
- 定位界面保持约 15 秒后自动返回正常监测界面

### 5. GNSS 定位

- 通过 Quectel GNSS 接口获取定位信息
- 支持显示定位状态
- 定位成功后显示经纬度
- 室内环境可能出现定位中状态，室外空旷区域更容易获取有效定位

### 6. TCP 数据上传

- 通过 TCP 连接远程服务器
- 定时上传温湿度、加速度、碰撞状态、碰撞次数、峰值和定位信息
- TCP 连接失败后会周期性重连
- 数据发送失败后会释放连接并等待下一次重连

### 7. LED 状态提示

- 通过 LED 周期闪烁表示系统运行状态
- 可作为本地运行状态指示

---

## 二、代码结构

当前项目主要文件结构如下：

```text
2026qiansai/
├── README.md           # 项目说明文档
├── main.py             # 主程序入口，负责系统初始化和循环调度
├── config.py           # 系统配置文件，包含服务器 IP、端口和周期参数
├── aht20_module.py     # AHT20 温湿度采集模块
├── app_module.py       # 应用层数据整合与上传模块
├── crash_module.py     # 加速度采集与碰撞检测模块
├── gnss_module.py      # GNSS 定位模块
├── lcd_module.py       # LCD 显示模块
├── led_module.py       # LED 状态提示模块
└── tcp_module.py       # TCP 通信模块
```

> 注意：`lcd_module.py` 中使用了 `from images1 import Quectel_Icon_160x20`，因此实际运行时还需要提供 `images1.py` 文件，用于存放 LCD 开机 Logo 图片数据。

---

## 三、模块说明

### 1. `main.py`

`main.py` 是系统主入口文件，负责完成各模块初始化和主循环任务调度。

主要流程如下：

```text
系统上电
↓
LCD 初始化并显示 Quectel Logo
↓
初始化 AHT20 温湿度模块
↓
初始化 LIS2DH12 碰撞检测模块
↓
初始化 GNSS 定位模块
↓
初始化 TCP 通信模块
↓
进入循环任务
↓
周期性执行 TCP、温湿度、碰撞检测、GNSS、数据上传和 LCD 刷新
```

在程序运行过程中，如果 GNSS 初始化失败，系统会继续运行其他功能，避免定位模块异常导致整个系统无法启动。

---

### 2. `config.py`

`config.py` 用于保存系统配置参数，例如服务器 IP、端口号和运行周期。

当前配置示例：

```python
SERVER_IP = "101.37.104.185"
SERVER_PORT = 42687

UPLOAD_INTERVAL_MS = 2000
MAIN_LOOP_DELAY_MS = 50
```

其中：

| 参数 | 说明 |
|---|---|
| `SERVER_IP` | TCP 服务器 IP 地址 |
| `SERVER_PORT` | TCP 服务器端口号 |
| `UPLOAD_INTERVAL_MS` | 数据上传间隔 |
| `MAIN_LOOP_DELAY_MS` | 主循环延时 |

---

### 3. `aht20_module.py`

该模块负责 AHT20 温湿度传感器的数据采集。

主要功能：

- 初始化 I2C 总线
- 扫描 I2C 设备
- 初始化 AHT20 传感器
- 周期性读取温度和湿度
- 提供 `get_data()` 接口给其他模块调用

主要接口：

```python
init()
task()
get_data()
```

---

### 4. `crash_module.py`

该模块负责加速度采集和碰撞检测。

主要功能：

- 初始化 LIS2DH12 加速度传感器
- 周期性读取三轴加速度
- 计算合加速度
- 根据阈值判断碰撞事件
- 记录碰撞次数和峰值
- 提供碰撞状态给 LCD 和上传模块使用

核心参数：

```python
CRASH_THRESHOLD = 35.0
_read_interval_ms = 20
_crash_cooldown_ms = 3000
```

其中：

| 参数 | 说明 |
|---|---|
| `CRASH_THRESHOLD` | 碰撞判断阈值，单位 m/s² |
| `_read_interval_ms` | 加速度采样间隔 |
| `_crash_cooldown_ms` | 碰撞冷却时间，避免重复触发 |

主要接口：

```python
init()
task()
get_data()
get_crash()
clear_crash()
```

---

### 5. `gnss_module.py`

该模块负责 GNSS 定位数据获取。

主要功能：

- 初始化 Quectel GNSS
- 启动定位功能
- 周期性读取经纬度
- 保存定位状态
- 提供定位数据给 LCD 和上传模块使用

主要接口：

```python
init()
task()
has_fix()
get_data()
close()
```

定位成功后可获取：

```text
latitude
longitude
has_fix
```

如果未定位成功，LCD 会显示 `SEARCH`，经纬度显示为 `--`。

---

### 6. `tcp_module.py`

该模块负责 TCP 网络连接和数据发送。

主要功能：

- 创建 TCP Socket
- 连接远程服务器
- 周期性重连
- 发送数据字符串
- 发送失败后自动关闭连接并等待重连

主要接口：

```python
init()
task()
connect()
send_line(text)
is_connected()
close()
```

TCP 连接状态会显示在 LCD 上：

```text
TCP: OK
```

或：

```text
TCP: NO
```

---

### 7. `app_module.py`

该模块负责整合各传感器数据，并通过 TCP 上传。

数据来源包括：

- AHT20 温度
- AHT20 湿度
- LIS2DH12 合加速度
- 碰撞状态
- 碰撞次数
- 碰撞峰值
- GNSS 定位状态
- 纬度
- 经度

上传数据格式示例：

```text
temp=26.5,hum=55.2,acc=9.81,crash=0,count=0,peak=0.00,gps=1,lat=30.123456,lon=104.123456
```

当检测到碰撞并且数据上传成功后，模块会调用 `crash_module.clear_crash()` 清除本次碰撞标志，但碰撞次数仍然保留，便于 LCD 显示碰撞记录。

---

### 8. `lcd_module.py`

该模块负责 LCD 界面显示，是本项目的人机交互核心模块。

主要显示界面包括：

#### 启动画面

系统上电后显示 Quectel Logo，保持约 5 秒。

#### 正常监测界面

正常运行时显示：

```text
Sensor & Crash
Temp:  xx.xC
Humi:  xx.x%
Acc:   xx.x
Crash: NO/YES count
TCP:   OK/NO
```

#### 碰撞定位界面

检测到碰撞后显示：

```text
Crash Detected
GPS:  FIX/SEARCH
Lat:  xx.xxxxxx
Lon:  xxx.xxxxxx
Cnt:  碰撞次数
Peak: 加速度峰值
```

LCD 界面切换逻辑：

- 默认显示正常监测界面
- 当碰撞次数增加时，切换到碰撞定位界面
- 碰撞定位界面保持约 15 秒
- 超时后自动返回正常监测界面

---

### 9. `led_module.py`

该模块负责 LED 状态提示。

主要功能：

- 初始化红色 LED
- 每 500 ms 翻转一次 LED 状态
- 用于指示系统正在运行

主要接口：

```python
init()
task()
```

---

## 四、系统运行流程

完整运行流程如下：

```text
1. 系统上电
2. 自动运行 main.py
3. LCD 显示 Quectel Logo
4. 延时约 5 秒
5. 初始化温湿度、加速度、GNSS 和 TCP 模块
6. LCD 切换到正常监测界面
7. 周期性采集温湿度和加速度数据
8. 周期性尝试 TCP 连接和数据上传
9. 周期性获取 GNSS 定位信息
10. 检测到碰撞后切换至定位界面
11. 显示 GPS 状态、经纬度、碰撞次数和峰值
12. 定位界面保持一段时间后返回正常监测界面
```

---

## 五、运行方法

### 1. 上传代码

将项目中的所有 `.py` 文件上传至开发板根目录，确保主程序文件名为：

```text
main.py
```

开发板上电或复位后会自动运行 `main.py`。

### 2. 检查配置

根据实际服务器信息修改 `config.py`：

```python
SERVER_IP = "服务器IP地址"
SERVER_PORT = 服务器端口号
```

### 3. 检查依赖文件

如果使用 LCD Logo 显示功能，需要确保开发板中存在：

```text
images1.py
```

并且其中定义了：

```python
Quectel_Icon_160x20
```

否则 `lcd_module.py` 在导入时会报错。

### 4. 上电运行

上电后正常现象为：

```text
1. LCD 显示 Quectel Logo
2. 5 秒后进入 Sensor & Crash 数据界面
3. 传感器数据周期性刷新
4. TCP 状态显示 OK 或 NO
5. 发生碰撞后切换到 Crash Detected 定位界面
```

---

## 六、测试建议

### 1. LCD 测试

上电后观察 LCD 是否显示 Quectel Logo，并在 5 秒后切换到数据界面。

### 2. 温湿度测试

用手靠近温湿度传感器或对传感器附近轻微哈气，观察温湿度数据是否变化。

### 3. 碰撞检测测试

轻敲头盔或开发板，观察 LCD 是否切换至 `Crash Detected` 界面。

### 4. GNSS 测试

GNSS 建议在室外空旷区域测试。室内可能出现长时间 `SEARCH` 状态。

### 5. TCP 测试

确认服务器 IP 和端口号正确，并观察 LCD 上的 TCP 状态是否变为 `OK`。

---

## 七、注意事项

1. **供电需要稳定**
   - 建议使用稳定的 5V 电源
   - 通信模块、LCD 和 GNSS 同时工作时电流需求较大
   - 供电不足可能导致重启、LCD 闪烁或 TCP/GNSS 异常

2. **GNSS 室内可能无法定位**
   - 室内信号较弱时会显示 `SEARCH`
   - 建议在室外空旷区域进行定位测试

3. **服务器端口必须一致**
   - `config.py` 中的端口号必须与实际 TCP 服务端口一致

4. **主程序文件名必须为 `main.py`**
   - 如果文件名不是 `main.py`，开发板上电后可能无法自动运行

5. **如果程序卡住**
   - 可通过串口工具按 `Ctrl + C` 中断
   - 必要时将 `main.py` 改名为 `main_bak.py` 后分模块调试

6. **LCD Logo 依赖图片数据文件**
   - 当前 `lcd_module.py` 依赖 `images1.py`
   - 上传代码时不要遗漏该文件

---

## 八、项目应用场景

本项目适用于骑行安全监测、智能头盔终端、户外运动保护、事故辅助定位和应急救援等场景。系统能够在骑行过程中实时采集环境与运动状态，在发生碰撞后自动显示定位信息，并通过网络上传关键数据，为事故后的快速定位和救援响应提供参考。

---

## 九、项目关键词

```text
智能骑行头盔
碰撞检测
GNSS定位
TCP通信
嵌入式系统
骑行安全
应急救援
```
