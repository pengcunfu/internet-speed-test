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
            ('https://api.ip.sb/ip', 'text'),  # IP.SB - 纯文本
            ('https://ipinfo.io/ip', 'text'),  # IPInfo - 纯文本
            ('https://api.ipify.org?format=text', 'text'),  # IPify - 纯文本
            ('http://myip.ipip.net/s', 'text'),  # IPIP.NET - 纯文本
        ]
        
        for service, format_type in ip_services:
            try:
                print(f"[IP查询] 尝试从 {service} 获取IP...")
                response = requests.get(service, timeout=5)
                response.raise_for_status()
                
                if format_type == 'text':
                    ip = response.text.strip()
                    print(f"[IP查询] 成功获取IP: {ip}")
                    return ip
                else:
                    data = response.json()
                    if 'ip' in data:
                        ip = data['ip']
                        print(f"[IP查询] 成功获取IP: {ip}")
                        return ip
            except Exception as e:
                print(f"[IP查询] 从 {service} 获取IP失败: {e}")
                continue
        
        print("[IP查询] 所有服务都失败")
        return None
            
    def get_ip_info_primary(self, ip: str) -> Optional[Dict]:
        """
        获取IP详细信息（使用国内API）
        
        Args:
            ip: IP地址
            
        Returns:
            Optional[Dict]: IP信息字典，失败返回None
        """
        # 备用：使用IP.SB
        try:
            print(f"[IP信息] 尝试从 IP.SB 查询 {ip} 的信息...")
            response = requests.get(
                f'https://api.ip.sb/geoip/{ip}',
                timeout=self._timeout
            )
            response.raise_for_status()
            data = response.json()
            
            result = {
                "ip": data.get("ip", ip),
                "country": data.get("country", "未知"),
                "countryCode": data.get("country_code", "未知"),
                "city": data.get("city", "未知"),
                "region": data.get("region", "未知"),
                "isp": data.get("isp", "未知"),
                "timezone": data.get("timezone", "未知")
            }
            print(f"[IP信息] 成功获取: {result['country']} {result['city']}")
            return result
        except Exception as e:
            print(f"[IP信息] IP.SB 查询失败: {e}")
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
