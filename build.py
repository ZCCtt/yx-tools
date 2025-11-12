#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare SpeedTest 多平台打包工具
支持：
- 普通打包（Linux/macOS/Windows，动态链接）
- OpenWRT 静态打包（ARM64，musl libc 兼容）
"""

import sys
import io
import os
import platform
import subprocess

# 修复 Windows 控制台中文编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_necessary_files():
    """检查必要文件是否存在"""
    if not os.path.exists("cloudflare_speedtest.py"):
        print("❌ 错误：未找到主脚本 'cloudflare_speedtest.py'")
        return False
    if not os.path.exists("requirements.txt"):
        print("⚠️ 警告：未找到 'requirements.txt'，将跳过项目依赖安装")
    return True

def install_system_dependencies(is_static=False):
    """安装系统级依赖（仅在 Linux/macOS 且静态打包时需要）"""
    if not is_static:
        return True  # 普通打包无需额外系统依赖
    
    system = platform.system().lower()
    if system != 'linux':
        print("⚠️ 静态打包仅支持 Linux 环境，将跳过系统依赖安装")
        return True
    
    print("\n正在安装静态打包所需系统依赖...")
    try:
        # 判断包管理器（apt 或 apk）
        if os.path.exists("/etc/apt"):
            subprocess.check_call([
                "sudo", "apt", "update",
                "&&", "sudo", "apt", "install", "-y",
                "build-essential", "zlib1g-dev", "openssl-dev", "musl-dev"
            ])
        elif os.path.exists("/etc/apk"):
            subprocess.check_call([
                "apk", "add", "--no-cache",
                "build-base", "zlib-dev", "openssl-dev", "musl-dev"
            ])
        print("✓ 系统依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 系统依赖安装失败: {e}")
        return False

def install_python_dependencies(is_static=False):
    """安装 Python 依赖（含 PyInstaller）"""
    print("\n正在安装 Python 依赖...")
    try:
        # 升级 pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安装 PyInstaller
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # 安装项目依赖（如果有 requirements.txt）
        if os.path.exists("requirements.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✓ Python 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Python 依赖安装失败: {e}")
        return False

def get_platform_info():
    """获取当前平台和架构信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # 系统映射
    os_map = {
        "darwin": "macos",
        "linux": "linux",
        "windows": "windows"
    }

    # 架构映射
    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "x64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
        "armv7l": "armhf",
        "armv8l": "armhf"
    }

    return os_map.get(system, system), arch_map.get(machine, machine)

def build_executable(is_static=False):
    """执行打包（支持普通打包和静态打包）"""
    os_name, arch = get_platform_info()
    
    # 静态打包强制命名（用于 OpenWRT 识别）
    if is_static:
        output_name = f"CloudflareSpeedTest-linux-arm64-static"
        print(f"\n" + "="*60)
        print(f"开始静态打包 Linux ARM64 版本（OpenWRT 兼容）")
        print(f"输出文件名: {output_name}")
        print("="*60)
    else:
        output_name = f"CloudflareSpeedTest-{os_name}-{arch}"
        print(f"\n" + "="*60)
        print(f"开始打包 {os_name}-{arch} 版本")
        print(f"输出文件名: {output_name}")
        print("="*60)

    # PyInstaller 基础参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 单文件打包
        "--name", output_name,          # 输出文件名
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 自动覆盖
        "--strip",                      # 去除调试符号（Linux/macOS）
        "--optimize", "2",              # 代码优化级别
        "--console",                    # 控制台程序
        # 隐藏导入（确保依赖被打包）
        "--hidden-import", "requests",
        "--hidden-import", "urllib3",
        "--hidden-import", "certifi",
        "--hidden-import", "charset_normalizer",
        "--hidden-import", "idna",
        # 排除不必要的模块
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",
        "--exclude-module", "PIL",
        "--exclude-module", "cv2",
        "cloudflare_speedtest.py"       # 主脚本
    ]

    # 静态打包额外参数（仅 Linux ARM64）
    if is_static:
        cmd.extend([
            "--target-architecture", "arm64",  # 指定 ARM64 架构
            "--distpath", "dist",              # 输出目录
            "--workpath", "build"              # 工作目录
        ])

    try:
        subprocess.check_call(cmd)
        print(f"\n" + "="*60)
        print(f"✓ 打包成功！可执行文件位置: dist/{output_name}")
        print("="*60)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 打包失败: {e}")
        return False

def main():
    """主函数（支持 --static 参数触发静态打包）"""
    print("="*60)
    print("Cloudflare SpeedTest 多平台打包工具")
    print("="*60)

    # 解析命令行参数（是否静态打包）
    is_static = "--static" in sys.argv

    # 1. 检查必要文件
    if not check_necessary_files():
        sys.exit(1)

    # 2. 安装系统依赖（仅静态打包需要）
    if is_static and not install_system_dependencies(is_static=True):
        sys.exit(1)

    # 3. 安装 Python 依赖
    if not install_python_dependencies(is_static=is_static):
        sys.exit(1)

    # 4. 执行打包
    if not build_executable(is_static=is_static):
        sys.exit(1)

    print("\n🎉 所有打包任务完成！")
    sys.exit(0)

if __name__ == "__main__":
    main()
