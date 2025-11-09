# -*- coding: utf-8 -*-
"""
IP Model
IP信息查询数据模型
"""

import requests
from typing import Dict, Optional


class IPModel:
    """IP信息模型类"""
    
    def __init__(self):
        """初始化模型"""
        self._timeout = 10
        
    def get_current_ip(self) -> Optional[str]:
        """
        获取当前公网IP地址
        
        Returns:
            Optional[str]: IP地址，失败返回None
        """
        try:
            response = requests.get(
                'https://api64.ipify.org?format=json',
                timeout=self._timeout
            )
            return response.json().get("ip")
        except Exception as e:
            print(f"获取IP失败: {e}")
            return None
            
    def get_ip_info_primary(self, ip: str) -> Optional[Dict]:
        """
        获取IP详细信息（主要API）
        
        Args:
            ip: IP地址
            
        Returns:
            Optional[Dict]: IP信息字典，失败返回None
        """
        try:
            response = requests.get(
                f'http://ip-api.com/json/{ip}',
                timeout=self._timeout
            )
            data = response.json()
            
            return {
                "ip": data.get("query"),
                "country": data.get("country"),
                "countryCode": data.get("countryCode"),
                "city": data.get("city"),
                "region": data.get("regionName"),
                "isp": data.get("isp"),
                "timezone": data.get("timezone")
            }
        except Exception as e:
            print(f"获取IP信息失败(主API): {e}")
            return None
            
    def get_ip_info_fallback(self, ip: str) -> Optional[Dict]:
        """
        获取IP详细信息（备用API）
        
        Args:
            ip: IP地址
            
        Returns:
            Optional[Dict]: IP信息字典，失败返回None
        """
        try:
            response = requests.get(
                f"https://ipapi.co/{ip}/json/",
                timeout=self._timeout
            )
            data = response.json()
            
            return {
                "ip": ip,
                "country": data.get("country_name"),
                "countryCode": data.get("country_code"),
                "city": data.get("city"),
                "region": data.get("region"),
                "isp": data.get("org"),
                "timezone": data.get("timezone")
            }
        except Exception as e:
            print(f"获取IP信息失败(备用API): {e}")
            return None
            
    def get_ip_info(self, ip: str) -> Optional[Dict]:
        """
        获取IP详细信息（自动尝试主备API）
        
        Args:
            ip: IP地址
            
        Returns:
            Optional[Dict]: IP信息字典，失败返回None
        """
        # 先尝试主API
        info = self.get_ip_info_primary(ip)
        if info:
            return info
            
        # 主API失败，尝试备用API
        return self.get_ip_info_fallback(ip)
