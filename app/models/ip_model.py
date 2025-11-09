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
        获取当前公网IP地址（使用国内服务）
        
        Returns:
            Optional[str]: IP地址，失败返回None
        """
        # 国内IP查询服务列表
        ip_services = [
            'https://myip.ipip.net/json',  # IPIP.NET
            'https://api.ip.sb/ip',  # IP.SB
            'https://ipinfo.io/ip',  # IPInfo
            'https://api.ipify.org?format=text',  # IPify备用
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                if 'json' in service:
                    data = response.json()
                    # IPIP.NET返回格式
                    if 'data' in data and 'ip' in data['data']:
                        return data['data']['ip']
                    # 其他JSON格式
                    elif 'ip' in data:
                        return data['ip']
                else:
                    # 纯文本格式
                    return response.text.strip()
            except Exception as e:
                print(f"从 {service} 获取IP失败: {e}")
                continue
        
        return None
            
    def get_ip_info_primary(self, ip: str) -> Optional[Dict]:
        """
        获取IP详细信息（使用国内API）
        
        Args:
            ip: IP地址
            
        Returns:
            Optional[Dict]: IP信息字典，失败返回None
        """
        try:
            # 使用IPIP.NET的API（国内服务）
            response = requests.get(
                f'https://myip.ipip.net/json/{ip}',
                timeout=self._timeout
            )
            data = response.json()
            
            if 'data' in data:
                info = data['data']
                return {
                    "ip": ip,
                    "country": info.get("country", "未知"),
                    "countryCode": info.get("country_code", "未知"),
                    "city": info.get("city", "未知"),
                    "region": info.get("province", "未知"),
                    "isp": info.get("isp", "未知"),
                    "timezone": info.get("timezone", "未知")
                }
        except Exception as e:
            print(f"获取IP信息失败(IPIP.NET): {e}")
            
        # 备用：使用IP.SB
        try:
            response = requests.get(
                f'https://api.ip.sb/geoip/{ip}',
                timeout=self._timeout
            )
            data = response.json()
            
            return {
                "ip": data.get("ip", ip),
                "country": data.get("country", "未知"),
                "countryCode": data.get("country_code", "未知"),
                "city": data.get("city", "未知"),
                "region": data.get("region", "未知"),
                "isp": data.get("isp", "未知"),
                "timezone": data.get("timezone", "未知")
            }
        except Exception as e:
            print(f"获取IP信息失败(IP.SB): {e}")
            return None
            
    def get_ip_info_fallback(self, ip: str) -> Optional[Dict]:
        """
        获取IP详细信息（国际备用API）
        
        Args:
            ip: IP地址
            
        Returns:
            Optional[Dict]: IP信息字典，失败返回None
        """
        # 尝试IPInfo.io
        try:
            response = requests.get(
                f"https://ipinfo.io/{ip}/json",
                timeout=self._timeout
            )
            data = response.json()
            
            return {
                "ip": data.get("ip", ip),
                "country": data.get("country", "未知"),
                "countryCode": data.get("country", "未知"),
                "city": data.get("city", "未知"),
                "region": data.get("region", "未知"),
                "isp": data.get("org", "未知"),
                "timezone": data.get("timezone", "未知")
            }
        except Exception as e:
            print(f"获取IP信息失败(IPInfo): {e}")
            
        # 最后备用：ip-api.com
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip}?lang=zh-CN",
                timeout=self._timeout
            )
            data = response.json()
            
            return {
                "ip": data.get("query", ip),
                "country": data.get("country", "未知"),
                "countryCode": data.get("countryCode", "未知"),
                "city": data.get("city", "未知"),
                "region": data.get("regionName", "未知"),
                "isp": data.get("isp", "未知"),
                "timezone": data.get("timezone", "未知")
            }
        except Exception as e:
            print(f"获取IP信息失败(ip-api): {e}")
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
