# -*- coding: utf-8 -*-
"""
Network Info Model
网络信息模型 - 获取网络适配器、代理等信息
"""

import psutil
import socket
import platform
import winreg
from typing import List, Dict, Optional


class NetworkInfoModel:
    """网络信息模型类"""
    
    def __init__(self):
        """初始化"""
        pass
        
    def get_network_adapters(self) -> List[Dict]:
        """
        获取网络适配器信息
        
        Returns:
            List[Dict]: 网络适配器列表
        """
        adapters = []
        
        try:
            # 获取所有网络接口
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                adapter_info = {
                    'name': interface_name,
                    'addresses': [],
                    'status': 'unknown',
                    'speed': 0
                }
                
                # 获取状态和速度
                if interface_name in stats:
                    stat = stats[interface_name]
                    adapter_info['status'] = 'up' if stat.isup else 'down'
                    adapter_info['speed'] = stat.speed  # Mbps
                
                # 获取IP地址
                for addr in addresses:
                    addr_info = {
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    
                    # 格式化地址族
                    if addr.family == socket.AF_INET:
                        addr_info['type'] = 'IPv4'
                    elif addr.family == socket.AF_INET6:
                        addr_info['type'] = 'IPv6'
                    elif addr.family == psutil.AF_LINK:
                        addr_info['type'] = 'MAC'
                    else:
                        addr_info['type'] = 'Other'
                    
                    adapter_info['addresses'].append(addr_info)
                
                adapters.append(adapter_info)
                
        except Exception as e:
            print(f"获取网络适配器信息失败: {e}")
            
        return adapters
        
    def get_proxy_settings(self) -> Dict:
        """
        获取系统代理设置（Windows）
        
        Returns:
            Dict: 代理设置信息
        """
        proxy_info = {
            'enabled': False,
            'http_proxy': None,
            'https_proxy': None,
            'ftp_proxy': None,
            'socks_proxy': None,
            'bypass_list': []
        }
        
        try:
            if platform.system() == 'Windows':
                # 读取Windows注册表
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
                )
                
                try:
                    proxy_enable, _ = winreg.QueryValueEx(key, 'ProxyEnable')
                    proxy_info['enabled'] = bool(proxy_enable)
                except:
                    pass
                
                try:
                    proxy_server, _ = winreg.QueryValueEx(key, 'ProxyServer')
                    if proxy_server:
                        # 解析代理服务器
                        if '=' in proxy_server:
                            # 格式: http=proxy:port;https=proxy:port
                            for item in proxy_server.split(';'):
                                if '=' in item:
                                    protocol, server = item.split('=', 1)
                                    proxy_info[f'{protocol}_proxy'] = server
                        else:
                            # 格式: proxy:port（所有协议使用同一代理）
                            proxy_info['http_proxy'] = proxy_server
                            proxy_info['https_proxy'] = proxy_server
                except:
                    pass
                
                try:
                    proxy_override, _ = winreg.QueryValueEx(key, 'ProxyOverride')
                    if proxy_override:
                        proxy_info['bypass_list'] = proxy_override.split(';')
                except:
                    pass
                
                winreg.CloseKey(key)
                
        except Exception as e:
            print(f"获取代理设置失败: {e}")
            
        return proxy_info
        
    def get_network_stats(self) -> Dict:
        """
        获取网络统计信息
        
        Returns:
            Dict: 网络统计信息
        """
        stats = {
            'bytes_sent': 0,
            'bytes_recv': 0,
            'packets_sent': 0,
            'packets_recv': 0,
            'errin': 0,
            'errout': 0,
            'dropin': 0,
            'dropout': 0
        }
        
        try:
            net_io = psutil.net_io_counters()
            stats['bytes_sent'] = net_io.bytes_sent
            stats['bytes_recv'] = net_io.bytes_recv
            stats['packets_sent'] = net_io.packets_sent
            stats['packets_recv'] = net_io.packets_recv
            stats['errin'] = net_io.errin
            stats['errout'] = net_io.errout
            stats['dropin'] = net_io.dropin
            stats['dropout'] = net_io.dropout
        except Exception as e:
            print(f"获取网络统计信息失败: {e}")
            
        return stats
        
    def get_dns_servers(self) -> List[str]:
        """
        获取DNS服务器列表
        
        Returns:
            List[str]: DNS服务器列表
        """
        dns_servers = []
        
        try:
            if platform.system() == 'Windows':
                import subprocess
                result = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
                
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'DNS' in line and ':' in line:
                        dns = line.split(':', 1)[1].strip()
                        if dns and dns not in dns_servers:
                            dns_servers.append(dns)
        except Exception as e:
            print(f"获取DNS服务器失败: {e}")
            
        return dns_servers
