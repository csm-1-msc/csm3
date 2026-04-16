# 传感器实时监控系统

基于 Python 内置库 + 纯 H5/CSS/JS 实现的传感器实时监控界面，支持 3D 姿态显示和 2D 仪表盘。

## 技术栈

- **后端**: Python 内置库（http.server, socketserver），无任何 Web 框架
- **前端**: 纯 HTML5 + CSS3 + JavaScript
- **3D 渲染**: Three.js 最小可用版（本地）
- **图表**: ECharts 简化离线版（本地）
- **数据更新频率**: 10Hz

## 文件结构

```
SensorMonitor/
├── index.html          # 前端界面（含 3D/2D 姿态模块）
├── echarts.min.js      # ECharts 离线版
├── three.min.js        # Three.js 最小版
├── sensor_server.py    # Python 数据服务器
└── README.md           # 项目说明
```

## 运行方法

### 步骤 1：启动 Python 服务器

在项目目录打开命令行，执行：

```bash
cd SensorMonitor
python sensor_server.py
```

或使用批处理脚本（如果已创建）：

```bash
run_server.bat
```

### 步骤 2：打开浏览器

访问：http://localhost:8080

### 步骤 3：停止服务器

按 `Ctrl+C` 停止 Python 服务器

## 功能模块

### 1. 实时数据显示
- 加速度（X/Y/Z 轴）
- 角速度（X/Y/Z 轴）
- 欧拉角（Roll/Pitch/Yaw）

### 2. 3D 设备姿态
- 实时 3D 立方体显示
- 根据 Roll/Pitch/Yaw 同步旋转
- 显示 X/Y/Z 坐标轴

### 3. 2D 姿态仪表盘
- 圆形仪表盘显示倾斜角度
- 倾斜方向指示（平放/左倾/右倾/前倾/后倾）

### 4. 实时波形图
- 加速度波形图
- 角速度波形图
- 欧拉角波形图

### 5. 姿态判断
- 当前姿态识别（平放/左倾/右倾/前倾/后倾/倒置）
- 运动状态判定（静止/正常移动/剧烈运动）
- 姿态保持时间计时（HH:MM:SS）

### 6. 数据导出
- 导出当前帧 JSON
- 导出机器学习数据集 CSV（最近 500 条记录）

## 姿态判定规则

| 姿态 | 判定条件 |
|------|----------|
| 平放 | \|Roll\| < 10° 且 \|Pitch\| < 10° |
| 左倾 | Roll < -10° |
| 右倾 | Roll > 10° |
| 前倾 | Pitch < -10° |
| 后倾 | Pitch > 10° |
| 倒置 | Pitch > 80° 或 Z 轴加速度 < -0.5g |

## 运动状态判定

基于最近 10 帧加速度三轴数据的标准差：
- **静止**: 标准差 < 0.05g
- **正常移动**: 标准差 0.05g ~ 0.2g
- **剧烈运动**: 标准差 > 0.2g

## 防抖机制

- **姿态防抖**: 5 帧滑动窗口，连续 5 帧一致才更新显示
- **状态防抖**: 3 帧滑动窗口，连续 3 帧一致才更新显示
- **滞回区间**: 10°阈值附近设置 1°滞回区（9°~11°），避免频繁跳变

## API 接口

| 接口 | 说明 |
|------|------|
| GET /api/sensor | 获取传感器数据（JSON） |
| GET /api/status | 获取服务器状态 |
| GET / | 访问前端界面 |

## 注意事项

1. 确保 Python 环境已安装（Python 3.x）
2. 服务器启动后，8080 端口将被占用
3. 数据源为模拟数据，可根据需要修改 `sensor_server.py` 中的 `SensorDataSimulator` 类
4. 全程离线运行，无需联网

## 自定义数据源

如需连接真实传感器，修改 `sensor_server.py` 中的 `get_data()` 方法：

```python
def get_data(self):
    # 替换为真实传感器数据读取逻辑
    return {
        "acceleration": {"x": 0.0, "y": 0.0, "z": 1.0},
        "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
        "euler_angle": {"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
        "timestamp": datetime.now().isoformat()
    }