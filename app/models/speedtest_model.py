# -*- coding: utf-8 -*-
"""
SpeedTest Model
网速测试数据模型
"""

import speedtest
from datetime import datetime
from typing import Dict, Optional


class SpeedTestModel:
    """网速测试模型类"""
    
    def __init__(self):
        """初始化模型"""
        self._speedtest_instance: Optional[speedtest.Speedtest] = None
        self._server_info: Optional[Dict] = None
        self._last_results: Dict = {}
        
    def initialize(self) -> bool:
        """
        初始化speedtest实例
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self._speedtest_instance = speedtest.Speedtest(secure=True)
            return True
        except Exception as e:
            print(f"初始化speedtest失败: {e}")
            return False
            
    def get_servers(self) -> bool:
        """
        获取服务器列表
        
        Returns:
            bool: 是否成功获取服务器列表
        """
        if not self._speedtest_instance:
            return False
            
        try:
            self._speedtest_instance.get_servers()
            return True
        except Exception as e:
            print(f"获取服务器列表失败: {e}")
            return False
            
    def select_best_server(self) -> Optional[Dict]:
        """
        选择最佳服务器
        
        Returns:
            Optional[Dict]: 服务器信息，失败返回None
        """
        if not self._speedtest_instance:
            return None
            
        try:
            self._speedtest_instance.get_best_server()
            self._server_info = self._speedtest_instance.results.server
            return self._server_info
        except Exception as e:
            print(f"选择最佳服务器失败: {e}")
            return None
            
    def test_download(self) -> Optional[float]:
        """
        测试下载速度
        
        Returns:
            Optional[float]: 下载速度(Mbps)，失败返回None
        """
        if not self._speedtest_instance:
            return None
            
        try:
            download_bps = self._speedtest_instance.download()
            download_mbps = round(download_bps / 1000000, 3)
            self._last_results['download'] = download_mbps
            self._last_results['download_time'] = datetime.now()
            return download_mbps
        except Exception as e:
            print(f"下载速度测试失败: {e}")
            return None
            
    def test_upload(self) -> Optional[float]:
        """
        测试上传速度
        
        Returns:
            Optional[float]: 上传速度(Mbps)，失败返回None
        """
        if not self._speedtest_instance:
            return None
            
        try:
            upload_bps = self._speedtest_instance.upload()
            upload_mbps = round(upload_bps / 1000000, 3)
            self._last_results['upload'] = upload_mbps
            self._last_results['upload_time'] = datetime.now()
            return upload_mbps
        except Exception as e:
            print(f"上传速度测试失败: {e}")
            return None
            
    def get_ping(self) -> Optional[float]:
        """
        获取Ping值
        
        Returns:
            Optional[float]: Ping值(ms)，失败返回None
        """
        if not self._speedtest_instance or not self._speedtest_instance.results.ping:
            return None
            
        try:
            ping = round(self._speedtest_instance.results.ping, 1)
            self._last_results['ping'] = ping
            self._last_results['ping_time'] = datetime.now()
            return ping
        except Exception as e:
            print(f"获取Ping失败: {e}")
            return None
            
    def get_server_info(self) -> Optional[Dict]:
        """
        获取服务器信息
        
        Returns:
            Optional[Dict]: 服务器信息
        """
        return self._server_info
        
    def get_last_results(self) -> Dict:
        """
        获取最后的测试结果
        
        Returns:
            Dict: 测试结果字典
        """
        return self._last_results.copy()
        
    def reset(self):
        """重置模型状态"""
        self._speedtest_instance = None
        self._server_info = None
        self._last_results.clear()
