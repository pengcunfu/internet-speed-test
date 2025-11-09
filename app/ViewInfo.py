# -*- coding: utf-8 -*-
"""
ViewInfo Dialog for Internet Speed Test
网速测试信息显示对话框 - PySide6版本
"""

import sys
import threading
import ctypes
import pyperclip
import requests
import speedtest
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTextEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

# 全局speedtest对象
speed = None

def init_speedtest():
    """初始化speedtest对象"""
    global speed
    try:
        speed = speedtest.Speedtest()
        return True
    except Exception as e:
        print(f"初始化speedtest失败: {e}")
        return False

class WorkerThread(QThread):
    """工作线程类"""
    
    # 定义信号
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, service, ip=None):
        super().__init__()
        self.service = service
        self.ip = ip
        self._is_running = True
        
    def run(self):
        """线程运行函数"""
        try:
            self.load_info()
        except Exception as e:
            self.error.emit(f"操作失败: {str(e)}")
            
    def load_info(self):
        """加载信息的函数"""
        global speed
        
        if not self._is_running:
            return
            
        # 初始化speedtest对象
        if self.service in ("download", "upload", "download and upload", "ping"):
            if not init_speedtest():
                self.error.emit("无法初始化网速测试服务")
                return
            try:
                self.progress.emit("正在连接测试服务器...")
                speed.get_best_server()
            except Exception as e:
                self.error.emit(f"连接测试服务器失败: {str(e)}")
                return
                
        if not self._is_running:
            return

        # 下载速度测试
        if self.service == "download":
            try:
                self.progress.emit("正在测试下载速度...")
                download_speed = round(speed.download()/1000000, 3)
                result = f"""网速测试完成！

下载速度: {download_speed} Mbps
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(f"下载速度测试失败: {str(e)}")

        # 上传速度测试
        elif self.service == "upload":
            try:
                self.progress.emit("正在测试上传速度...")
                upload_speed = round(speed.upload()/1000000, 3)
                result = f"""网速测试完成！

上传速度: {upload_speed} Mbps
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(f"上传速度测试失败: {str(e)}")

        # 完整速度测试
        elif self.service == "download and upload":
            try:
                self.progress.emit("正在测试下载速度...")
                download_speed = round(speed.download()/1000000, 3)
                
                if not self._is_running:
                    return
                    
                self.progress.emit("正在测试上传速度...")
                upload_speed = round(speed.upload()/1000000, 3)
                
                result = f"""完整网速测试完成！

下载速度: {download_speed} Mbps
上传速度: {upload_speed} Mbps
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(f"速度测试失败: {str(e)}")

        # Ping测试
        elif self.service == "ping":
            try:
                self.progress.emit("正在测试Ping...")
                ping = round(speed.results.ping, 1)
                result = f"""Ping测试完成！

延迟: {ping} ms
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(f"Ping测试失败: {str(e)}")

        # 获取当前IP
        elif self.service == "get ip":
            try:
                self.progress.emit("正在获取IP地址...")
                ip = get_ip()
                self.finished.emit(f"您的IP地址是: {ip}")
            except Exception as e:
                self.error.emit(f"获取IP失败: {str(e)}")

        # 获取当前IP信息
        elif self.service == "ip info":
            try:
                self.progress.emit("正在获取IP信息...")
                ip = get_ip()
                try:
                    info = get_ip_information(ip)
                except:
                    info = get_location(ip)
                
                result = f"""IP信息查询完成！

IP地址: {info.get("ip", "未知")}
国家: {info.get("country", "未知")}
国家代码: {info.get("countryCode", "未知")}
城市: {info.get("city", "未知")}
地区: {info.get("region", "未知")}
"""
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(f"获取IP信息失败: {str(e)}")

        # 获取外部IP信息
        elif self.service == "get external IP Info":
            try:
                self.progress.emit("正在查询外部IP信息...")
                ip = self.ip
                try:
                    info = get_ip_information(ip)
                except:
                    info = get_location(ip)
                
                result = f"""外部IP信息查询完成！

IP地址: {info.get("ip", "未知")}
国家: {info.get("country", "未知")}  
国家代码: {info.get("countryCode", "未知")}
城市: {info.get("city", "未知")}
地区: {info.get("region", "未知")}
"""
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(f"查询外部IP信息失败: {str(e)}")
                
    def stop(self):
        """停止线程"""
        self._is_running = False
        self.quit()
        self.wait()

class ViewInfoDialog(QDialog):
    """信息查看对话框"""
    
    def __init__(self, parent, service, ip=None):
        super().__init__(parent)
        self.service = service
        self.ip = ip
        self.worker_thread = None
        
        self.setWindowTitle('信息查看')
        self.setFixedSize(450, 500)
        self.setModal(True)
        
        # 居中显示
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        
        self.init_ui()
        self.start_loading()
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置背景色
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(250, 250, 250))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        self.title_label = QLabel("正在加载，请稍候...")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #323296;")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 信息显示区域
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("复制信息")
        self.close_btn = QPushButton("关闭")
        
        # 设置按钮样式
        button_style = """
        QPushButton {
            font-size: 11px;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        """
        
        self.copy_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #64b464;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #5aa45a;
            }
        """)
        
        self.close_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: 1px solid #c0c0c0;
            }
        """)
        
        button_layout.addWidget(self.copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        # 添加到主布局
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.info_text)
        main_layout.addLayout(button_layout)
        
        # 绑定事件
        self.copy_btn.clicked.connect(self.copy_info)
        self.close_btn.clicked.connect(self.close_dialog)
        
    def start_loading(self):
        """开始加载"""
        self.worker_thread = WorkerThread(self.service, self.ip)
        self.worker_thread.finished.connect(self.on_finished)
        self.worker_thread.error.connect(self.on_error)
        self.worker_thread.progress.connect(self.on_progress)
        self.worker_thread.start()
        
    def on_progress(self, message):
        """更新进度"""
        self.title_label.setText(message)
        self.info_text.setText(f"{message}\n\n请耐心等待...")
        
    def on_finished(self, result):
        """处理完成"""
        self.title_label.setText("信息已加载")
        self.info_text.setText(result)
        
    def on_error(self, error_message):
        """处理错误"""
        self.title_label.setText("发生错误")
        self.info_text.setText(f"错误: {error_message}")
        
    def copy_info(self):
        """复制信息到剪贴板"""
        try:
            text = self.info_text.toPlainText()
            pyperclip.copy(text)
            QMessageBox.information(self, "提示", "信息已复制到剪贴板")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"复制失败: {str(e)}")
        
    def close_dialog(self):
        """关闭对话框"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
        self.accept()
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
        event.accept()

# 获取IP地址的函数
def get_ip():
    """获取当前公网IP地址"""
    response = requests.get('https://api64.ipify.org?format=json', timeout=10).json()
    return response["ip"]

def get_location(ip):
    """获取IP位置信息"""
    ip_address = ip
    response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=10).json()
    location_data = {
        "ip": ip_address,
        "country": response.get("country_name"),
        "countryCode": response.get("country_code"),
        "city": response.get("city"),
        "region": response.get("region")
    }
    return location_data

def get_ip_information(ip):
    """获取IP详细信息"""
    response = requests.get(f'http://ip-api.com/json/{ip}', timeout=10).json()
    location_data = {
        "ip": response.get("query"),
        "country": response.get("country"),
        "countryCode": response.get("countryCode"),
        "city": response.get("city"),
        "region": response.get("regionName")
    }
    return location_data