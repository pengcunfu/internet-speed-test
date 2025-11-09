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
from PIL import Image


def clean_build_dirs():
    """清理之前的编译目录"""
    dirs_to_clean = ['build', 'dist', 'main.build', 'main.dist', 'main.onefile-build']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"正在清理目录: {dir_name}")
            shutil.rmtree(dir_name)


def convert_png_to_ico():
    """将PNG图标转换为ICO格式"""
    png_path = Path('resources/icon.png')
    ico_path = Path('resources/icon.ico')
    
    if not png_path.exists():
        print("⚠ 未找到图标文件: resources/icon.png")
        return False
    
    if ico_path.exists():
        print(f"✓ 图标文件已存在: {ico_path}")
        return True
    
    try:
        print(f"正在转换图标: {png_path} -> {ico_path}")
        img = Image.open(png_path)
        # 转换为RGBA模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        # 保存为ICO格式，包含多个尺寸
        img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"✓ 图标转换成功: {ico_path}")
        return True
    except ImportError:
        print("✗ 需要安装Pillow库来转换图标")
        print("请运行: pip install Pillow")
        return False
    except Exception as e:
        print(f"✗ 图标转换失败: {e}")
        return False


def check_nuitka():
    """检查Nuitka是否已安装"""
    try:
        result = subprocess.run([sys.executable, '-m', 'nuitka', '--version'], 
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
    
    # 检查并转换图标
    icon_path = Path('resources/icon.ico')
    if not icon_path.exists():
        print("\n正在准备图标文件...")
        convert_png_to_ico()
    
    # Nuitka编译参数（非独立模式，启动更快）
    nuitka_args = [
        sys.executable,
        '-m',
        'nuitka',
        '--windows-disable-console',       # Windows下隐藏控制台窗口（GUI程序）
        '--enable-plugin=pyside6',         # 启用PySide6插件
        '--follow-imports',                # 跟踪所有导入
        '--assume-yes-for-downloads',      # 自动下载依赖
        '--output-dir=dist',               # 输出目录
        '--company-name=PengCunfu',        # 公司名称
        '--product-name=Internet Speed Test Tool',  # 产品名称
        '--file-version=1.0.0.0',          # 文件版本
        '--product-version=1.0.0',         # 产品版本
        '--file-description=Internet Speed Test Tool - 网速测试工具',  # 文件描述
        '--copyright=Copyright (c) 2024',  # 版权信息
    ]
    
    # 添加图标参数（如果存在）
    if icon_path.exists():
        nuitka_args.append(f'--windows-icon-from-ico={icon_path}')
        print(f"✓ 使用图标: {icon_path}")
    
    # 添加入口文件
    nuitka_args.append('main.py')
    
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
        exe_path = Path('dist') / 'main.exe'
        if exe_path.exists():
            # 重命名为InternetSpeedTest.exe
            final_path = Path('dist') / 'InternetSpeedTest.exe'
            if final_path.exists():
                final_path.unlink()
            exe_path.rename(final_path)
            
            size_mb = final_path.stat().st_size / (1024 * 1024)
            print(f"\n生成的exe文件:")
            print(f"  路径: {final_path.absolute()}")
            print(f"  大小: {size_mb:.2f} MB")
            print(f"\n注意: 非独立模式需要Python环境才能运行")
            print(f"  - 启动速度更快")
            print(f"  - 文件体积更小")
            print(f"  - 需要在有Python环境的机器上运行")
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
        print("  2. 非独立模式：启动快，但需要Python环境")
        print("  3. 图标已集成到exe文件中")
        return 0
    else:
        print("\n编译失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
