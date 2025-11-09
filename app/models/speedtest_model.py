# -*- coding: utf-8 -*-
"""
SpeedTest Model
网速测试数据模型
"""

import speedtest
import subprocess
import platform
from datetime import datetime
from typing import Dict, Optional, List


class SpeedTestModel:
    """网速测试模型类"""
    
    # 国内主要测速服务器ID列表
    CHINA_SERVERS = [
        3633,   # 中国电信 - 上海
        5505,   # 中国联通 - 上海
        5145,   # 中国移动 - 上海
        4870,   # 中国电信 - 北京
        4713,   # 中国联通 - 北京
        4575,   # 中国移动 - 北京
        4647,   # 中国电信 - 广州
        6132,   # 中国联通 - 广州
        4515,   # 中国移动 - 广州
        5017,   # 中国电信 - 深圳
        10201,  # 中国联通 - 深圳
        4884,   # 中国移动 - 深圳
        5083,   # 中国电信 - 成都
        5726,   # 中国联通 - 成都
        4624,   # 中国移动 - 成都
    ]
    
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
            
    def get_servers(self, use_china_servers: bool = True) -> bool:
        """
        获取服务器列表（优先使用预配置的国内服务器）
        
        Args:
            use_china_servers: 是否使用预配置的国内服务器
            
        Returns:
            bool: 是否成功获取服务器列表
        """
        if not self._speedtest_instance:
            return False
            
        try:
            if use_china_servers:
                print(f"[测速服务器] 尝试使用预配置的 {len(self.CHINA_SERVERS)} 个国内服务器...")
                try:
                    # 使用预配置的国内服务器ID
                    self._speedtest_instance.get_servers(self.CHINA_SERVERS)
                    
                    if hasattr(self._speedtest_instance, 'servers') and self._speedtest_instance.servers:
                        server_count = sum(len(s) for s in self._speedtest_instance.servers.values())
                        if server_count > 0:
                            print(f"[测速服务器] 成功加载 {server_count} 个国内服务器")
                            
                            # 显示可用的服务器
                            shown = 0
                            for distance, servers in sorted(self._speedtest_instance.servers.items()):
                                for server in servers:
                                    if shown < 5:  # 显示前5个
                                        print(f"  - {server.get('sponsor', '未知')} ({server.get('name', '未知')}, {server.get('country', '未知')})")
                                        shown += 1
                            
                            return True
                except Exception as e:
                    print(f"[测速服务器] 预配置服务器加载失败: {e}")
            
            # 如果预配置失败或不使用，则自动获取
            print(f"[测速服务器] 正在自动获取服务器列表...")
            self._speedtest_instance.get_servers([])  # 获取所有服务器
            
            if hasattr(self._speedtest_instance, 'servers') and self._speedtest_instance.servers:
                all_servers = self._speedtest_instance.servers
                total_count = sum(len(s) for s in all_servers.values())
                print(f"[测速服务器] 获取到 {total_count} 个服务器")
                
                # 尝试筛选中国和香港服务器
                filtered_servers = {}
                for key, servers in all_servers.items():
                    # 包含中国大陆和香港的服务器
                    country_servers = [s for s in servers if s.get('cc', '') in ['CN', 'HK']]
                    if country_servers:
                        filtered_servers[key] = country_servers
                
                if filtered_servers:
                    cn_count = sum(len(s) for s in filtered_servers.values())
                    self._speedtest_instance.servers = filtered_servers
                    print(f"[测速服务器] 已筛选到 {cn_count} 个中国/香港服务器")
                    
                    # 显示部分服务器
                    shown = 0
                    for distance, servers in sorted(filtered_servers.items()):
                        for server in servers:
                            if shown < 5:
                                print(f"  - {server.get('sponsor', '未知')} ({server.get('name', '未知')}, {server.get('country', '未知')})")
                                shown += 1
                else:
                    print(f"[测速服务器] 未找到中国服务器，使用全球服务器")
            
            return True
        except Exception as e:
            print(f"[测速服务器] 获取服务器列表失败: {e}")
            import traceback
            traceback.print_exc()
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
            print(f"[测速服务器] 正在测试服务器延迟，选择最佳服务器...")
            self._speedtest_instance.get_best_server()
            self._server_info = self._speedtest_instance.results.server
            
            print(f"[测速服务器] 已选择最佳服务器:")
            print(f"  - 名称: {self._server_info.get('sponsor', '未知')}")
            print(f"  - 位置: {self._server_info.get('name', '未知')}, {self._server_info.get('country', '未知')}")
            print(f"  - 距离: {self._server_info.get('d', 0):.2f} km")
            print(f"  - 延迟: {self._speedtest_instance.results.ping:.2f} ms")
            
            return self._server_info
        except Exception as e:
            print(f"[测速服务器] 选择最佳服务器失败: {e}")
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
            print(f"[下载测试] 开始测试下载速度...")
            download_bps = self._speedtest_instance.download()
            download_mbps = round(download_bps / 1000000, 3)
            self._last_results['download'] = download_mbps
            self._last_results['download_time'] = datetime.now()
            
            print(f"[下载测试] 下载速度: {download_mbps} Mbps ({download_bps / 1024 / 1024:.2f} MB/s)")
            return download_mbps
        except Exception as e:
            print(f"[下载测试] 下载速度测试失败: {e}")
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
            print(f"[上传测试] 开始测试上传速度...")
            upload_bps = self._speedtest_instance.upload()
            upload_mbps = round(upload_bps / 1000000, 3)
            self._last_results['upload'] = upload_mbps
            self._last_results['upload_time'] = datetime.now()
            
            print(f"[上传测试] 上传速度: {upload_mbps} Mbps ({upload_bps / 1024 / 1024:.2f} MB/s)")
            return upload_mbps
        except Exception as e:
            print(f"[上传测试] 上传速度测试失败: {e}")
            return None
            
    def get_ping(self) -> Optional[float]:
        """
        获取Ping值（从speedtest服务器）
        
        Returns:
            Optional[float]: Ping值(ms)，失败返回None
        """
        if not self._speedtest_instance or not self._speedtest_instance.results.ping:
            return None
            
        try:
            ping = round(self._speedtest_instance.results.ping, 1)
            self._last_results['ping'] = ping
            self._last_results['ping_time'] = datetime.now()
            
            print(f"[Ping测试] 到测速服务器的延迟: {ping} ms")
            return ping
        except Exception as e:
            print(f"[Ping测试] 获取Ping失败: {e}")
            return None
            
    def ping_multiple_hosts(self, hosts: List[str] = None) -> Optional[Dict]:
        """
        Ping多个主机并计算平均延迟（国内常用服务）
        
        Args:
            hosts: 主机列表，默认使用国内常用服务
            
        Returns:
            Optional[Dict]: 包含各主机延迟和平均值的字典
        """
        if hosts is None:
            # 国内常用服务器
            hosts = [
                ('114.114.114.114', '114DNS'),
                ('223.5.5.5', '阿里DNS'),
                ('119.29.29.29', '腾讯DNS'),
                ('180.76.76.76', '百度DNS'),
                ('1.2.4.8', 'CNNIC DNS'),
            ]
        
        print(f"[Ping测试] 开始测试 {len(hosts)} 个国内服务器的延迟...")
        
        results = {}
        valid_pings = []
        
        for host_info in hosts:
            if isinstance(host_info, tuple):
                host, name = host_info
            else:
                host, name = host_info, host_info
                
            ping_time = self._ping_host(host)
            results[name] = ping_time
            
            if ping_time is not None:
                valid_pings.append(ping_time)
                print(f"[Ping测试] {name} ({host}): {ping_time:.1f} ms")
            else:
                print(f"[Ping测试] {name} ({host}): 超时")
        
        if valid_pings:
            avg_ping = round(sum(valid_pings) / len(valid_pings), 1)
            min_ping = round(min(valid_pings), 1)
            max_ping = round(max(valid_pings), 1)
            
            print(f"[Ping测试] 统计结果:")
            print(f"  - 平均延迟: {avg_ping} ms")
            print(f"  - 最小延迟: {min_ping} ms")
            print(f"  - 最大延迟: {max_ping} ms")
            print(f"  - 成功率: {len(valid_pings)}/{len(hosts)}")
            
            return {
                'results': results,
                'average': avg_ping,
                'min': min_ping,
                'max': max_ping,
                'success_count': len(valid_pings),
                'total_count': len(hosts)
            }
        else:
            print(f"[Ping测试] 所有主机都无法访问")
            return None
            
    def _ping_host(self, host: str, count: int = 4) -> Optional[float]:
        """
        Ping单个主机
        
        Args:
            host: 主机地址
            count: ping次数
            
        Returns:
            Optional[float]: 平均延迟(ms)，失败返回None
        """
        try:
            # 根据操作系统选择ping命令
            system = platform.system().lower()
            if system == 'windows':
                cmd = ['ping', '-n', str(count), '-w', '1000', host]
            else:
                cmd = ['ping', '-c', str(count), '-W', '1', host]
            
            # 执行ping命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 解析ping结果
                output = result.stdout
                if system == 'windows':
                    # Windows: 平均 = XXms
                    for line in output.split('\n'):
                        if '平均' in line or 'Average' in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                avg_str = parts[-1].strip().replace('ms', '').strip()
                                return float(avg_str)
                else:
                    # Linux/Mac: rtt min/avg/max/mdev = XX/XX/XX/XX ms
                    for line in output.split('\n'):
                        if 'rtt' in line or 'round-trip' in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                values = parts[1].split('/')
                                if len(values) >= 2:
                                    return float(values[1])
            
            return None
        except Exception as e:
            print(f"[Ping测试] Ping {host} 失败: {e}")
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
