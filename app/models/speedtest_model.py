# -*- coding: utf-8 -*-
"""
SpeedTest Model
网速测试数据模型
"""

import subprocess
import platform
from datetime import datetime
from typing import Dict, Optional, List
from .simple_speedtest import SimpleSpeedTest


class SpeedTestModel:
    """网速测试模型类（使用自实现的HTTP测速）"""
    
    def __init__(self, log_callback=None):
        """初始化模型"""
        self._simple_speedtest: SimpleSpeedTest = None
        self._last_results: Dict = {}
        self._log_callback = log_callback  # 日志回调函数
        
    def _log(self, message: str):
        """输出日志"""
        print(message)  # 仍然打印到控制台
        if self._log_callback:
            self._log_callback(message)  # 同时发送到界面
        
    def initialize(self) -> bool:
        """
        初始化测速实例
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self._log("[初始化] 使用HTTP直接测速模式")
            self._simple_speedtest = SimpleSpeedTest(log_callback=self._log_callback)
            return True
        except Exception as e:
            self._log(f"[初始化] 初始化失败: {e}")
            return False
            
    def get_servers(self, use_china_servers: bool = True) -> bool:
        """
        准备测速（使用HTTP直接测速）
        
        Args:
            use_china_servers: 兼容参数，已不使用
            
        Returns:
            bool: 总是返回True
        """
        self._log("[测速准备] 使用国内CDN和网站进行HTTP直接测速")
        return True
            
    def select_best_server(self) -> Optional[Dict]:
        """
        选择最佳服务器（HTTP模式不需要）
        
        Returns:
            Optional[Dict]: 返回空字典表示准备就绪
        """
        self._log("[测速准备] 准备就绪，开始测速")
        return {}
            
    def test_download(self) -> Optional[float]:
        """
        测试下载速度
        
        Returns:
            Optional[float]: 下载速度(Mbps)，失败返回None
        """
        if self._simple_speedtest:
            return self._simple_speedtest.test_download()
        return None
            
    def test_upload(self) -> Optional[float]:
        """
        测试上传速度
        
        Returns:
            Optional[float]: 上传速度(Mbps)，失败返回None
        """
        if self._simple_speedtest:
            return self._simple_speedtest.test_upload()
        return None
            
    def get_ping(self) -> Optional[float]:
        """
        获取Ping值（不再使用）
        
        Returns:
            Optional[float]: Ping值(ms)，失败返回None
        """
        return None
            
    def ping_multiple_hosts(self, hosts: List[str] = None) -> Optional[Dict]:
        """
        Ping多个主机并计算平均延迟（国内常用服务）
        
        Args:
            hosts: 主机列表，默认使用国内常用服务
            
        Returns:
            Optional[Dict]: 包含各主机延迟和平均值的字典
        """
        if self._simple_speedtest:
            return self._simple_speedtest.test_ping()
        return None
            
    def get_server_info(self) -> Optional[Dict]:
        """
        获取服务器信息
        
        Returns:
            Optional[Dict]: 服务器信息（HTTP模式返回空）
        """
        return {}
        
    def get_last_results(self) -> Dict:
        """
        获取最后的测试结果
        
        Returns:
            Dict: 测试结果字典
        """
        return self._last_results.copy()
        
    def reset(self):
        """重置模型状态"""
        if self._simple_speedtest:
            self._simple_speedtest.cleanup()
        self._simple_speedtest = None
        self._last_results.clear()
        
    def cleanup(self):
        """清理资源"""
        if self._simple_speedtest:
            self._simple_speedtest.cleanup()
            
    def __del__(self):
        """析构函数"""
        self.cleanup()
