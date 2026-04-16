# 传感器实时监控系统

基于 Python 内置库 + 纯 H5/CSS/JS 实现的传感器实时监控界面，支持 3D 姿态显示和 2D 仪表盘。

## 技术栈

- **后端**: Python 内置库（http.server, socketserver），无任何 Web 框架依赖
- **前端**: 纯 HTML5 + CSS3 + JavaScript
- **3D 渲染**: Three.js 最小可用版（本地）
- **图表**: ECharts 简化离线版（本地）
- **数据更新频率**: 10Hz

## 文件结构

```
SensorMonitor/
├── index.html          # 前端页面（含 3D/2D 姿态模块、波形图、姿态判断）
├── echarts.min.js      # ECharts 离线版
├── three.min.js        # Three.js 最小版
├── sensor_server.py    # Python 数据服务器（模拟传感器数据）
├── run_server.bat      # Windows 快速启动脚本
└── README.md           # 项目说明文档
```

## 运行方法

### 方法 1：使用批处理脚本（推荐）

双击 `run_server.bat` 文件即可启动服务器。

### 方法 2：命令行启动

```bash
cd SensorMonitor
python sensor_server.py
```

### 访问系统

打开浏览器访问：http://localhost:8080

### 停止服务器

按 `Ctrl+C` 停止 Python 服务器

## 功能模块

### 1. 实时数据显示
- 加速度（X/Y/Z 轴，单位：g）
- 角速度（X/Y/Z 轴，单位：°/s）
- 欧拉角（Roll/Pitch/Yaw，单位：°）

### 2. 实时波形图
- 加速度波形图（三轴彩色曲线）
- 角速度波形图（三轴彩色曲线）

### 3. 3D 姿态显示
- 实时 3D 立方体姿态模拟
- 基于欧拉角旋转

### 4. 2D 仪表盘
- 水平仪（Roll）
- 俯仰仪（Pitch）

### 5. 姿态判断
- 正常、翻转、侧翻、俯仰等状态检测

## GitLab Flow 分支管理

本项目采用 GitLab Flow 分支管理策略：

### 分支说明

| 分支名 | 说明 | 保护状态 |
|--------|------|----------|
| `main` | 开发分支，日常开发工作 | 否 |
| `staging` | 预发布分支，测试环境部署 | 是 |
| `production` | 生产分支，正式环境部署 | 是 |

### 工作流程

```
feature 分支 (开发) → main 分支 (开发) → staging 分支 (测试) → production 分支 (生产)
```

1. **开发阶段**: 在 `main` 分支上进行日常开发
2. **测试阶段**: 代码稳定后合并到 `staging` 分支进行测试
3. **发布阶段**: 测试通过后合并到 `production` 分支发布

### 分支保护规则

- `staging` 分支：仅允许从 `main` 分支合并，需要代码审查
- `production` 分支：仅允许从 `staging` 分支合并，需要审批

## 开发说明

### 添加新传感器数据

在 `sensor_server.py` 中添加新的数据字段，并在 `index.html` 中对应的显示模块添加展示逻辑。

### 修改波形图

波形图配置在 `index.html` 中的 `initWaveformCharts()` 函数内，可修改颜色、范围等参数。

### 修改 3D 模型

3D 模型在 `init3DModel()` 函数中创建，可替换为更复杂的模型。

## 许可证

本项目仅供学习使用。