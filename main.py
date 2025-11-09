# -*- coding: utf-8 -*-
"""
Internet Speed Test Tool
基于Python和PySide6开发的网速测试小工具
MVC架构版本 - 优化性能，避免界面卡顿
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import SpeedTestApp

def main():
    """主函数"""
    # 创建并运行应用
    app = SpeedTestApp(sys.argv)
    sys.exit(app.run())

if __name__ == "__main__":
    main()