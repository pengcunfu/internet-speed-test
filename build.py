#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuitka Build Script for Internet Speed Test Tool
使用Nuitka编译Python程序为exe可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_dirs():
    """清理之前的编译目录"""
    dirs_to_clean = ['build', 'dist', 'main.build', 'main.dist', 'main.onefile-build']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"正在清理目录: {dir_name}")
            shutil.rmtree(dir_name)


def check_nuitka():
    """检查Nuitka是否已安装"""
    try:
        result = subprocess.run(['nuitka', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(f"✓ Nuitka 已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Nuitka 未安装")
        print("请运行: pip install nuitka")
        return False


def build_exe():
    """使用Nuitka编译exe"""
    print("\n" + "=" * 60)
    print("开始使用Nuitka编译...")
    print("=" * 60)
    
    # Nuitka编译参数
    nuitka_args = [
        'nuitka',
        '--standalone',                    # 独立模式，包含所有依赖
        '--onefile',                       # 单文件模式
        '--windows-disable-console',       # Windows下隐藏控制台窗口（GUI程序）
        '--enable-plugin=pyside6',         # 启用PySide6插件
        '--include-package=speedtest',     # 包含speedtest包
        '--include-package=requests',      # 包含requests包
        '--include-package=pyperclip',     # 包含pyperclip包
        '--include-package=urllib3',       # 包含urllib3包
        '--include-package=certifi',       # 包含certifi包
        '--include-package=charset_normalizer',  # 包含charset_normalizer包
        '--include-package=idna',          # 包含idna包
        '--follow-imports',                # 跟踪所有导入
        '--assume-yes-for-downloads',      # 自动下载依赖
        '--output-dir=dist',               # 输出目录
        '--output-filename=InternetSpeedTest.exe',  # 输出文件名
        '--company-name=PengCunfu',        # 公司名称
        '--product-name=Internet Speed Test Tool',  # 产品名称
        '--file-version=1.0.0.0',          # 文件版本
        '--product-version=1.0.0',         # 产品版本
        '--file-description=Internet Speed Test Tool - 网速测试工具',  # 文件描述
        '--copyright=Copyright (c) 2024',  # 版权信息
        '--windows-icon-from-ico=icon.ico' if os.path.exists('icon.ico') else '',  # 图标（如果存在）
        'main.py'                          # 入口文件
    ]
    
    # 移除空字符串参数
    nuitka_args = [arg for arg in nuitka_args if arg]
    
    print("\n编译命令:")
    print(' '.join(nuitka_args))
    print("\n")
    
    try:
        # 执行编译
        subprocess.run(nuitka_args, check=True)
        
        print("\n" + "=" * 60)
        print("✓ 编译成功！")
        print("=" * 60)
        
        # 检查输出文件
        exe_path = Path('dist') / 'InternetSpeedTest.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n生成的exe文件:")
            print(f"  路径: {exe_path.absolute()}")
            print(f"  大小: {size_mb:.2f} MB")
            return True
        else:
            print("\n✗ 未找到生成的exe文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"✗ 编译失败: {e}")
        print("=" * 60)
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Internet Speed Test Tool - Nuitka编译脚本")
    print("=" * 60)
    
    # 检查Nuitka
    if not check_nuitka():
        print("\n请先安装Nuitka:")
        print("  pip install nuitka")
        input("\n按回车键退出...")
        return 1
    
    # 清理旧的编译文件
    print("\n正在清理旧的编译文件...")
    clean_build_dirs()
    
    # 开始编译
    if build_exe():
        print("\n编译完成！可以在 dist 目录中找到生成的exe文件。")
        print("\n提示:")
        print("  1. 首次运行可能需要较长时间（下载依赖）")
        print("  2. 生成的exe文件可以在没有Python环境的Windows系统上运行")
        print("  3. 如果需要添加图标，请将icon.ico文件放在项目根目录")
        return 0
    else:
        print("\n编译失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
