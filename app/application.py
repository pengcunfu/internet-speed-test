# -*- coding: utf-8 -*-
"""
Application
应用程序主类
"""

from PySide6.QtWidgets import QApplication
from .views.main_window import MainWindow


class SpeedTestApp(QApplication):
    """网速测试应用程序类"""
    
    def __init__(self, argv):
        """
        初始化应用程序
        
        Args:
            argv: 命令行参数
        """
        super().__init__(argv)
        
        # 设置应用程序信息
        self.setApplicationName("网速测试工具")
        self.setApplicationVersion("2.1")
        self.setOrganizationName("SpeedTest")
        
        # 设置应用程序样式
        self.setStyle('Fusion')
        
        # 创建主窗口
        self.main_window = MainWindow()
        
    def run(self) -> int:
        """
        运行应用程序
        
        Returns:
            int: 退出代码
        """
        self.main_window.show()
        return self.exec()
