#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
传感器实时监控系统 - Python 数据服务器
基于 Python 内置库实现，无任何 Web 框架依赖
数据更新频率：10Hz
"""

import http.server
import socketserver
import json
import math
import os
import time
import threading
from datetime import datetime

# 配置
PORT = 8080
UPDATE_INTERVAL = 0.1  # 10Hz

# 模拟传感器数据状态
class SensorDataSimulator:
    def __init__(self):
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        # 姿态循环配置（每个姿态 3 秒）
        self.pose_cycle_duration = 3  # 秒
        self.poses = [
            {'name': '平放', 'roll': 0, 'pitch': 0, 'acc_z': 1.0},
            {'name': '左倾', 'roll': -25, 'pitch': 0, 'acc_z': 0.9},
            {'name': '右倾', 'roll': 25, 'pitch': 0, 'acc_z': 0.9},
            {'name': '前倾', 'roll': 0, 'pitch': -25, 'acc_z': 0.9},
            {'name': '后倾', 'roll': 0, 'pitch': 25, 'acc_z': 0.9},
            {'name': '倒置', 'roll': 0, 'pitch': 0, 'acc_z': -1.0}
        ]
        
        # 状态循环配置（每个状态 5 秒）
        self.motion_cycle_duration = 5  # 秒
        self.motion_states = [
            {'name': '静止', 'acc_noise': 0.02, 'gyro_noise': 2},
            {'name': '正常移动', 'acc_noise': 0.12, 'gyro_noise': 15},
            {'name': '剧烈运动', 'acc_noise': 0.35, 'gyro_noise': 40}
        ]
        
    def get_current_pose_target(self, elapsed_time):
        """获取当前时间对应的目标姿态"""
        pose_cycle_time = elapsed_time % (self.pose_cycle_duration * len(self.poses))
        pose_index = int(pose_cycle_time / self.pose_cycle_duration)
        return self.poses[pose_index]
    
    def get_current_motion_target(self, elapsed_time):
        """获取当前时间对应的目标运动状态"""
        motion_cycle_time = elapsed_time % (self.motion_cycle_duration * len(self.motion_states))
        motion_index = int(motion_cycle_time / self.motion_cycle_duration)
        return self.motion_states[motion_index]
    
    def lerp(self, start, end, t):
        """线性插值"""
        return start + (end - start) * t
    
    def get_data(self):
        """获取模拟的传感器数据"""
        with self.lock:
            elapsed_time = time.time() - self.start_time
            
            # 获取当前姿态目标和运动状态目标
            pose_target = self.get_current_pose_target(elapsed_time)
            motion_target = self.get_current_motion_target(elapsed_time)
            
            # 计算当前姿态周期内的进度（用于添加波动）
            pose_cycle_time = elapsed_time % (self.pose_cycle_duration * len(self.poses))
            pose_phase = (pose_cycle_time % self.pose_cycle_duration) / self.pose_cycle_duration
            
            # 计算当前运动周期内的进度
            motion_cycle_time = elapsed_time % (self.motion_cycle_duration * len(self.motion_states))
            motion_phase = (motion_cycle_time % self.motion_cycle_duration) / self.motion_cycle_duration
            
            # 基于目标姿态生成欧拉角（添加小幅波动）
            roll = pose_target['roll'] + 2 * math.sin(elapsed_time * 3)
            pitch = pose_target['pitch'] + 2 * math.cos(elapsed_time * 2.5)
            yaw = 10 * math.sin(elapsed_time * 0.2)  # Yaw 缓慢变化
            
            # 基于目标姿态和运动状态生成加速度
            base_acc_z = pose_target['acc_z']
            acc_x = motion_target['acc_noise'] * math.sin(elapsed_time * 5)
            acc_y = motion_target['acc_noise'] * math.cos(elapsed_time * 4)
            acc_z = base_acc_z + motion_target['acc_noise'] * 0.5 * math.sin(elapsed_time * 6)
            
            # 基于运动状态生成角速度
            gyro_base = motion_target['gyro_noise']
            gyro_x = gyro_base * math.sin(elapsed_time * 2 + motion_phase * math.pi)
            gyro_y = gyro_base * 0.8 * math.cos(elapsed_time * 1.5 + motion_phase * math.pi)
            gyro_z = gyro_base * 0.6 * math.sin(elapsed_time * 1 + motion_phase * math.pi)
            
            return {
                "acceleration": {
                    "x": round(acc_x, 4),
                    "y": round(acc_y, 4),
                    "z": round(acc_z, 4)
                },
                "angular_velocity": {
                    "x": round(gyro_x, 2),
                    "y": round(gyro_y, 2),
                    "z": round(gyro_z, 2)
                },
                "euler_angle": {
                    "roll": round(roll, 2),
                    "pitch": round(pitch, 2),
                    "yaw": round(yaw, 2)
                },
                "timestamp": datetime.now().isoformat()
            }

# 全局模拟器实例
simulator = SensorDataSimulator()

# 获取脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class SensorHandler(http.server.BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_GET(self):
        if self.path == '/api/sensor':
            self.send_sensor_data()
        elif self.path == '/api/status':
            self.send_status()
        elif self.path == '/' or self.path == '/index.html':
            self.serve_index()
        elif self.path == '/echarts.min.js' or self.path == '/three.min.js':
            self.serve_static_file()
        else:
            self.send_error(404)
    
    def serve_index(self):
        """提供 index.html 页面"""
        try:
            index_path = os.path.join(SCRIPT_DIR, 'index.html')
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, b'index.html not found')
    
    def serve_static_file(self):
        """提供静态文件（echarts.min.js, three.min.js）"""
        try:
            filename = self.path.lstrip('/')
            file_path = os.path.join(SCRIPT_DIR, filename)
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            if filename.endswith('.js'):
                self.send_header('Content-type', 'application/javascript; charset=utf-8')
            else:
                self.send_header('Content-type', 'application/octet-stream')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f'{filename} not found'.encode())
    
    def send_sensor_data(self):
        """发送传感器数据"""
        data = simulator.get_data()
        response = json.dumps(data, ensure_ascii=False)
        response_bytes = response.encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(response_bytes))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_bytes)
    
    def send_status(self):
        """发送服务器状态"""
        status = {
            "status": "running",
            "port": PORT,
            "update_rate": f"{1/UPDATE_INTERVAL}Hz",
            "timestamp": datetime.now().isoformat()
        }
        response = json.dumps(status, ensure_ascii=False)
        response_bytes = response.encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(response_bytes))
        self.end_headers()
        self.wfile.write(response_bytes)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """支持多线程的 TCP 服务器"""
    allow_reuse_address = True

def print_banner():
    """打印启动信息"""
    print("=" * 60)
    print("传感器实时监控系统 - 数据服务")
    print("=" * 60)
    print(f"服务器地址：http://localhost:{PORT}")
    print(f"数据接口：http://localhost:{PORT}/api/sensor")
    print(f"状态接口：http://localhost:{PORT}/api/status")
    print(f"数据源：模拟")
    print(f"更新间隔：{UPDATE_INTERVAL}秒")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()

def run_server():
    """运行服务器"""
    print_banner()
    
    with ThreadedTCPServer(("", PORT), SensorHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"错误：{e}")