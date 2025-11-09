# -*- coding: utf-8 -*-
"""
Main Window View
主窗口视图
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QGridLayout, QPushButton, QLabel, QInputDialog, 
                               QMessageBox, QMenu, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
from ..controllers.speedtest_controller import SpeedTestController
from ..controllers.ip_controller import IPController
from .result_dialog import ResultDialog


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 初始化控制器
        self.speedtest_controller = SpeedTestController()
        self.ip_controller = IPController()
        
        # 连接控制器信号
        self._connect_controller_signals()
        
        # 当前结果对话框
        self._current_dialog = None
        
        # 设置窗口
        self.setWindowTitle('网速测试工具 - Internet Speed Test')
        self.setFixedSize(600, 400)
        self._center_window()
        
        # 设置窗口图标
        try:
            self.setWindowIcon(QIcon.fromTheme("network-wireless"))
        except:
            pass
        
        # 初始化UI
        self._init_ui()
        
    def _center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def _connect_controller_signals(self):
        """连接控制器信号"""
        # 网速测试控制器信号
        self.speedtest_controller.progress_updated.connect(self._on_progress_updated)
        self.speedtest_controller.test_completed.connect(self._on_test_completed)
        self.speedtest_controller.test_failed.connect(self._on_test_failed)
        
        # IP控制器信号
        self.ip_controller.progress_updated.connect(self._on_progress_updated)
        self.ip_controller.query_completed.connect(self._on_query_completed)
        self.ip_controller.query_failed.connect(self._on_query_failed)
        
    def _init_ui(self):
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
        
        # 设置按钮样式
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
        QPushButton:disabled {
            background-color: #cccccc;
            color: #888888;
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
        self._bind_events()
        
    def _bind_events(self):
        """绑定事件"""
        self.download_btn.clicked.connect(lambda: self._start_speed_test('download'))
        self.upload_btn.clicked.connect(lambda: self._start_speed_test('upload'))
        self.both_btn.clicked.connect(lambda: self._start_speed_test('both'))
        self.ping_btn.clicked.connect(lambda: self._start_speed_test('ping'))
        self.ip_info_btn.clicked.connect(self._show_ip_menu)
        self.help_btn.clicked.connect(self._show_help_menu)
        self.close_btn.clicked.connect(self.close)
        
    def _start_speed_test(self, test_type: str):
        """
        开始速度测试
        
        Args:
            test_type: 测试类型
        """
        # 禁用所有按钮
        self._set_buttons_enabled(False)
        
        # 显示结果对话框
        self._current_dialog = ResultDialog(self, "网速测试")
        self._current_dialog.show()
        
        # 开始测试
        self.speedtest_controller.start_test(test_type)
        
    def _start_ip_query(self, query_type: str, ip: str = None):
        """
        开始IP查询
        
        Args:
            query_type: 查询类型
            ip: IP地址（可选）
        """
        # 禁用所有按钮
        self._set_buttons_enabled(False)
        
        # 显示结果对话框
        self._current_dialog = ResultDialog(self, "IP信息查询")
        self._current_dialog.show()
        
        # 开始查询
        if query_type == 'get_ip':
            self.ip_controller.get_current_ip()
        elif query_type == 'ip_info':
            self.ip_controller.get_current_ip_info()
        elif query_type == 'external_ip_info' and ip:
            self.ip_controller.get_external_ip_info(ip)
            
    def _on_progress_updated(self, message: str):
        """进度更新处理"""
        if self._current_dialog:
            self._current_dialog.update_progress(message)
            
    def _on_test_completed(self, result: dict):
        """测试完成处理"""
        if self._current_dialog:
            self._current_dialog.show_result(self._format_speed_test_result(result))
        self._set_buttons_enabled(True)
        
    def _on_test_failed(self, error_msg: str):
        """测试失败处理"""
        if self._current_dialog:
            self._current_dialog.show_error(error_msg)
        self._set_buttons_enabled(True)
        
    def _on_query_completed(self, result: dict):
        """查询完成处理"""
        if self._current_dialog:
            self._current_dialog.show_result(self._format_ip_result(result))
        self._set_buttons_enabled(True)
        
    def _on_query_failed(self, error_msg: str):
        """查询失败处理"""
        if self._current_dialog:
            self._current_dialog.show_error(error_msg)
        self._set_buttons_enabled(True)
        
    def _format_speed_test_result(self, result: dict) -> str:
        """
        格式化速度测试结果
        
        Args:
            result: 结果字典
            
        Returns:
            str: 格式化后的结果文本
        """
        lines = []
        
        if 'download' in result and 'upload' in result:
            lines.append("完整网速测试完成！\n")
            lines.append(f"下载速度: {result['download']} Mbps")
            lines.append(f"上传速度: {result['upload']} Mbps")
        elif 'download' in result:
            lines.append("下载速度测试完成！\n")
            lines.append(f"下载速度: {result['download']} Mbps")
        elif 'upload' in result:
            lines.append("上传速度测试完成！\n")
            lines.append(f"上传速度: {result['upload']} Mbps")
        elif 'ping' in result:
            lines.append("Ping测试完成！\n")
            lines.append(f"延迟: {result['ping']} ms")
            
        if 'timestamp' in result:
            lines.append(f"测试时间: {result['timestamp']}")
            
        return '\n'.join(lines)
        
    def _format_ip_result(self, result: dict) -> str:
        """
        格式化IP查询结果
        
        Args:
            result: 结果字典
            
        Returns:
            str: 格式化后的结果文本
        """
        if 'country' in result:
            # 详细信息
            lines = [
                "IP信息查询完成！\n",
                f"IP地址: {result.get('ip', '未知')}",
                f"国家: {result.get('country', '未知')}",
                f"国家代码: {result.get('countryCode', '未知')}",
                f"城市: {result.get('city', '未知')}",
                f"地区: {result.get('region', '未知')}"
            ]
            if 'isp' in result:
                lines.append(f"ISP: {result.get('isp', '未知')}")
            if 'timezone' in result:
                lines.append(f"时区: {result.get('timezone', '未知')}")
            return '\n'.join(lines)
        else:
            # 仅IP地址
            return f"您的IP地址是: {result.get('ip', '未知')}"
            
    def _set_buttons_enabled(self, enabled: bool):
        """
        设置按钮启用状态
        
        Args:
            enabled: 是否启用
        """
        self.download_btn.setEnabled(enabled)
        self.upload_btn.setEnabled(enabled)
        self.both_btn.setEnabled(enabled)
        self.ping_btn.setEnabled(enabled)
        self.ip_info_btn.setEnabled(enabled)
        
    def _show_ip_menu(self):
        """显示IP信息菜单"""
        menu = QMenu(self)
        
        get_my_ip_action = menu.addAction("获取我的IP")
        get_my_ip_info_action = menu.addAction("获取我的IP详细信息")
        get_external_ip_info_action = menu.addAction("查询外部IP信息")
        
        get_my_ip_action.triggered.connect(lambda: self._start_ip_query('get_ip'))
        get_my_ip_info_action.triggered.connect(lambda: self._start_ip_query('ip_info'))
        get_external_ip_info_action.triggered.connect(self._query_external_ip)
        
        # 在按钮下方显示菜单
        button_pos = self.ip_info_btn.mapToGlobal(self.ip_info_btn.rect().bottomLeft())
        menu.exec(button_pos)
        
    def _query_external_ip(self):
        """查询外部IP"""
        ip_address, ok = QInputDialog.getText(self, "外部IP查询", "请输入要查询的IP地址:")
        if ok and ip_address.strip():
            self._start_ip_query('external_ip_info', ip_address.strip())
        elif ok:
            QMessageBox.warning(self, "错误", "请输入有效的IP地址")
            
    def _show_help_menu(self):
        """显示帮助菜单"""
        menu = QMenu(self)
        
        help_action = menu.addAction("使用帮助")
        about_action = menu.addAction("关于")
        
        help_action.triggered.connect(self._show_help)
        about_action.triggered.connect(self._show_about)
        
        # 在按钮下方显示菜单
        button_pos = self.help_btn.mapToGlobal(self.help_btn.rect().bottomLeft())
        menu.exec(button_pos)
        
    def _show_help(self):
        """显示帮助"""
        help_text = """网速测试工具使用说明：

1. 下载速度测试：测试您的网络下载速度
2. 上传速度测试：测试您的网络上传速度  
3. 完整速度测试：同时测试下载和上传速度
4. Ping测试：测试网络延迟
5. IP信息：查看本机或其他IP的详细信息

注意：测试过程可能需要一些时间，请耐心等待。
所有测试都在后台线程运行，不会阻塞界面。"""
        
        QMessageBox.information(self, "使用帮助", help_text)
        
    def _show_about(self):
        """显示关于"""
        about_text = """网速测试工具 v0.0.2

基于Python和PySide6开发的网络速度测试工具。
采用MVC设计模式，优化了性能和用户体验。

特性：
- 异步测试，界面流畅不卡顿
- 清晰的MVC架构
- 完善的错误处理

开发语言：Python
图形界面：PySide6
网速测试：speedtest-cli
架构模式：MVC"""
        
        QMessageBox.information(self, "关于", about_text)
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 取消所有正在进行的操作
        self.speedtest_controller.cancel_test()
        self.ip_controller.cancel_query()
        event.accept()
