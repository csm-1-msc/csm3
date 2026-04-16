@echo off
chcp 65001 >nul
echo ============================================
echo 传感器实时监控系统 - 数据服务
echo ============================================
echo.

REM 检查端口 8080 是否被占用
netstat -ano | findstr ":8080" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 端口 8080 已被占用，正在尝试关闭旧进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080"') do (
        set PID=%%a
    )
    if defined PID (
        taskkill /F /PID %PID% >nul 2>&1
        timeout /t 2 /nobreak >nul
    )
)

echo 服务器地址：http://localhost:8080
echo 数据接口：http://localhost:8080/api/sensor
echo 状态接口：http://localhost:8080/api/status
echo 数据源：模拟
echo 更新间隔：0.1 秒 (10Hz)
echo ============================================
echo.
echo 按 Ctrl+C 停止服务器
echo ============================================
echo.

REM 启动服务器并自动打开浏览器
start "" "http://localhost:8080/"
python sensor_server.py

pause