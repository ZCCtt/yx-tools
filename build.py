#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare SpeedTest 自动打包工具
支持多平台、多架构可执行文件生成
"""

import sys
import io

# 修复 Windows 控制台中文编码问题
if sys.platform == 'win32':
    # 将标准输出和标准错误流设置为 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import platform
import subprocess

def check_and_install_pyinstaller():
    """检查并安装 PyInstaller"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装（版本: {PyInstaller.__version__}）")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装，正在尝试安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ PyInstaller 安装失败，请手动执行：pip install pyinstaller")
            return False

def install_project_dependencies():
    """安装项目依赖（从 requirements.txt）"""
    if not os.path.exists("requirements.txt"):
        print("⚠️ 未找到 requirements.txt，跳过依赖安装")
        return True
    print("\n正在安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 项目依赖安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ 项目依赖安装失败，请手动执行：pip install -r requirements.txt")
        return False

def build_executable():
    """打包可执行文件"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # 系统与架构映射
    os_map = {
        "darwin": "macos",
        "linux": "linux",
        "windows": "windows"
    }
    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "x64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
        "armv7l": "armhf",
        "armv8l": "armhf"
    }

    os_name = os_map.get(system, system)
    arch = arch_map.get(machine, machine)
    output_name = f"CloudflareSpeedTest-{os_name}-{arch}"

    print("\n" + "=" * 60)
    print(f"开始打包 {os_name}-{arch} 版本")
    print(f"输出文件名: {output_name}")
    print("=" * 60)

    # PyInstaller 命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 单文件打包
        "--name", output_name,          # 输出文件名
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 自动覆盖
        "--strip",                      # 去除调试符号
        "--optimize", "2",              # 代码优化级别
        "--console",                    # 控制台程序
        "cloudflare_speedtest.py"       # 主脚本路径
    ]

    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print(f"✓ 打包成功！可执行文件位置: dist/{output_name}")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 打包失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Cloudflare SpeedTest 自动打包工具")
    print("=" * 60)

    # 检查并安装 PyInstaller
    if not check_and_install_pyinstaller():
        sys.exit(1)

    # 安装项目依赖
    if not install_project_dependencies():
        sys.exit(1)

    # 执行打包
    if not build_executable():
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
