# -*- coding: utf-8 -*-
"""
Internet Speed Test GUI Application
网速测试图形界面应用程序 - PySide6版本
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                               QInputDialog, QMessageBox, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
import speedtest
import requests
import webbrowser
from ViewInfo import ViewInfoDialog

class SpeedTestWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('网速测试工具 - Internet Speed Test')
        self.setFixedSize(600, 400)
        self.center_window()
        
        # 设置窗口图标（如果有的话）
        try:
            self.setWindowIcon(QIcon.fromTheme("network-wireless"))
        except:
            pass
        
        self.init_ui()
        
    def center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 设置背景色
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        central_widget.setPalette(palette)
        central_widget.setAutoFillBackground(True)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("网速测试工具")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #323296;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 说明文字
        desc_label = QLabel("选择测试类型，点击按钮开始测试")
        desc_label.setStyleSheet("color: #646464;")
        desc_label.setAlignment(Qt.AlignCenter)
        
        # 创建按钮网格布局
        button_layout = QGridLayout()
        button_layout.setSpacing(15)
        
        # 创建按钮
        self.download_btn = QPushButton("下载速度测试")
        self.upload_btn = QPushButton("上传速度测试")
        self.both_btn = QPushButton("完整速度测试")
        self.ping_btn = QPushButton("Ping 测试")
        self.ip_info_btn = QPushButton("IP 信息")
        
        # 设置按钮大小和样式
        button_style = """
        QPushButton {
            font-size: 12px;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
            border: 2px solid transparent;
        }
        QPushButton:hover {
            border: 2px solid #ffffff;
        }
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 0.2);
        }
        """
        
        # 设置按钮样式和大小
        buttons = [
            (self.download_btn, "#64b464"),  # 绿色
            (self.upload_btn, "#6496dc"),   # 蓝色
            (self.both_btn, "#dc9664"),     # 橙色
            (self.ping_btn, "#c864c8"),     # 紫色
            (self.ip_info_btn, "#96c8c8")   # 青色
        ]
        
        for btn, color in buttons:
            btn.setFixedSize(150, 50)
            btn.setStyleSheet(button_style + f"QPushButton {{ background-color: {color}; color: white; }}")
        
        # 添加按钮到网格
        button_layout.addWidget(self.download_btn, 0, 0)
        button_layout.addWidget(self.upload_btn, 0, 1)
        button_layout.addWidget(self.both_btn, 1, 0, 1, 2)  # 跨两列
        button_layout.addWidget(self.ping_btn, 2, 0)
        button_layout.addWidget(self.ip_info_btn, 2, 1)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        self.help_btn = QPushButton("帮助")
        self.close_btn = QPushButton("退出")
        
        # 设置底部按钮样式
        bottom_button_style = """
        QPushButton {
            font-size: 11px;
            padding: 8px 16px;
            border-radius: 6px;
            background-color: #e0e0e0;
            border: 1px solid #c0c0c0;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        """
        
        self.help_btn.setStyleSheet(bottom_button_style)
        self.close_btn.setStyleSheet(bottom_button_style)
        
        bottom_layout.addWidget(self.help_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_btn)
        
        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)
        
        # 绑定事件
        self.bind_events()
        
    def bind_events(self):
        """绑定事件"""
        self.download_btn.clicked.connect(self.on_download_speed)
        self.upload_btn.clicked.connect(self.on_upload_speed)
        self.both_btn.clicked.connect(self.on_both_speed)
        self.ping_btn.clicked.connect(self.on_ping_test)
        self.ip_info_btn.clicked.connect(self.on_ip_info)
        self.help_btn.clicked.connect(self.on_help)
        self.close_btn.clicked.connect(self.close)
        
    def on_download_speed(self):
        """下载速度测试"""
        dialog = ViewInfoDialog(self, "download")
        dialog.exec()
        
    def on_upload_speed(self):
        """上传速度测试"""
        dialog = ViewInfoDialog(self, "upload")
        dialog.exec()
        
    def on_both_speed(self):
        """完整速度测试"""
        dialog = ViewInfoDialog(self, "download and upload")
        dialog.exec()
        
    def on_ping_test(self):
        """Ping测试"""
        dialog = ViewInfoDialog(self, "ping")
        dialog.exec()
        
    def on_ip_info(self):
        """IP信息菜单"""
        menu = QMenu(self)
        
        get_my_ip_action = menu.addAction("获取我的IP")
        get_my_ip_info_action = menu.addAction("获取我的IP详细信息")
        get_external_ip_info_action = menu.addAction("查询外部IP信息")
        
        get_my_ip_action.triggered.connect(self.on_get_my_ip)
        get_my_ip_info_action.triggered.connect(self.on_get_my_ip_info)
        get_external_ip_info_action.triggered.connect(self.on_get_external_ip_info)
        
        # 在按钮下方显示菜单
        button_pos = self.ip_info_btn.mapToGlobal(self.ip_info_btn.rect().bottomLeft())
        menu.exec(button_pos)
        
    def on_get_my_ip(self):
        """获取我的IP"""
        dialog = ViewInfoDialog(self, "get ip")
        dialog.exec()
        
    def on_get_my_ip_info(self):
        """获取我的IP详细信息"""
        dialog = ViewInfoDialog(self, "ip info")
        dialog.exec()
        
    def on_get_external_ip_info(self):
        """查询外部IP信息"""
        ip_address, ok = QInputDialog.getText(self, "外部IP查询", "请输入要查询的IP地址:")
        if ok and ip_address.strip():
            dialog = ViewInfoDialog(self, "get external IP Info", ip_address.strip())
            dialog.exec()
        elif ok:
            QMessageBox.warning(self, "错误", "请输入有效的IP地址")
        
    def on_help(self):
        """帮助菜单"""
        menu = QMenu(self)
        
        help_action = menu.addAction("使用帮助")
        about_action = menu.addAction("关于")
        
        help_action.triggered.connect(self.on_show_help)
        about_action.triggered.connect(self.on_about)
        
        # 在按钮下方显示菜单
        button_pos = self.help_btn.mapToGlobal(self.help_btn.rect().bottomLeft())
        menu.exec(button_pos)
        
    def on_show_help(self):
        """显示帮助"""
        help_text = """网速测试工具使用说明：

1. 下载速度测试：测试您的网络下载速度
2. 上传速度测试：测试您的网络上传速度  
3. 完整速度测试：同时测试下载和上传速度
4. Ping测试：测试网络延迟
5. IP信息：查看本机或其他IP的详细信息

注意：测试过程可能需要一些时间，请耐心等待。"""
        
        QMessageBox.information(self, "使用帮助", help_text)
        
    def on_about(self):
        """关于"""
        about_text = """网速测试工具 v2.0

基于Python和PySide6开发的网络速度测试工具。
可以测试网络的下载速度、上传速度、Ping值，
还可以查询IP地址的详细信息。

开发语言：Python
图形界面：PySide6
网速测试：speedtest-cli"""
        
        QMessageBox.information(self, "关于", about_text)

class SpeedTestApp(QApplication):
    """应用程序类"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("网速测试工具")
        self.setApplicationVersion("2.0")
        
        # 设置应用程序样式
        self.setStyle('Fusion')
        
        # 创建主窗口
        self.main_window = SpeedTestWindow()
        
    def run(self):
        """运行应用程序"""
        self.main_window.show()
        return self.exec()

# 如果直接运行此文件
if __name__ == "__main__":
    app = SpeedTestApp(sys.argv)
    sys.exit(app.run())