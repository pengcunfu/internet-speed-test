#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 网速测试工具
Launch Script - Internet Speed Test Tool
"""

import sys
import os

def check_dependencies():
    """检查依赖包是否安装"""
    try:
        import PySide6
        print("✓ PySide6 已安装")
    except ImportError:
        print("✗ PySide6 未安装，请运行: pip install PySide6")
        return False
        
    try:
        import speedtest
        print("✓ speedtest-cli 已安装")
    except ImportError:
        print("✗ speedtest-cli 未安装，请运行: pip install speedtest-cli")
        return False
        
    try:
        import requests
        print("✓ requests 已安装")
    except ImportError:
        print("✗ requests 未安装，请运行: pip install requests")
        return False
        
    try:
        import pyperclip
        print("✓ pyperclip 已安装")
    except ImportError:
        print("✗ pyperclip 未安装，请运行: pip install pyperclip")
        return False
        
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("网速测试工具 - Internet Speed Test Tool")
    print("=" * 50)
    print("正在检查依赖包...")
    
    if not check_dependencies():
        print("\n请安装缺失的依赖包，或运行:")
        print("pip install -r requirements.txt")
        input("\n按回车键退出...")
        return
        
    print("\n所有依赖包已就绪，正在启动程序...")
    
    # 导入并运行主程序
    try:
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"\n程序启动失败: {e}")
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()
