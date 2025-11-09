# -*- coding: utf-8 -*-
"""
Simple SpeedTest Implementation
简单的网速测试实现 - 不依赖speedtest-cli
"""

import time
import requests
import threading
import tempfile
import os
from typing import Optional, Dict
from datetime import datetime


class SimpleSpeedTest:
    """简单的网速测试类"""
    
    # 国内测速文件URL（使用CDN和适中大小的文件）
    TEST_URLS = {
        'download': [
            # 使用较小的测试文件，更快更可靠
            ('https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe', '200MB', '腾讯QQ下载'),
            ('https://mirrors.aliyun.com/ubuntu-releases/22.04/ubuntu-22.04.3-desktop-amd64.iso', '4GB', '阿里云Ubuntu镜像'),
            ('https://mirrors.163.com/ubuntu-releases/22.04/ubuntu-22.04.3-desktop-amd64.iso', '4GB', '网易Ubuntu镜像'),
            ('https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/22.04/ubuntu-22.04.3-desktop-amd64.iso', '4GB', '清华Ubuntu镜像'),
            ('https://mirrors.ustc.edu.cn/ubuntu-releases/22.04/ubuntu-22.04.3-desktop-amd64.iso', '4GB', '中科大Ubuntu镜像'),
            ('https://issuecdn.baidupcs.com/issue/netdisk/yunguanjia/BaiduNetdisk_7.17.0.12.exe', '100MB', '百度网盘客户端'),
            ('http://mirrors.sohu.com/ubuntu-releases/22.04/ubuntu-22.04.3-desktop-amd64.iso', '4GB', '搜狐Ubuntu镜像'),
            ('https://mirrors.huaweicloud.com/ubuntu-releases/22.04/ubuntu-22.04.3-desktop-amd64.iso', '4GB', '华为云Ubuntu镜像'),
        ],
        'upload': [
            # 使用国内测试接口
            ('https://httpbin.org/post', 'httpbin'),
            ('https://postman-echo.com/post', 'postman-echo'),
            ('http://httpbin.org/post', 'httpbin-http'),
        ]
    }
    
    def __init__(self, log_callback=None):
        """初始化"""
        self.download_speed = 0.0
        self.upload_speed = 0.0
        self.ping_time = 0.0
        self._log_callback = log_callback
        self._temp_files = []  # 存储临时文件路径
        self._downloaded_data = None  # 存储下载的数据用于上传测试
        
        # 详细统计信息
        self.download_stats = {
            'max': 0.0,
            'min': 0.0,
            'avg': 0.0,
            'speeds': []
        }
        self.upload_stats = {
            'max': 0.0,
            'min': 0.0,
            'avg': 0.0,
            'speeds': []
        }
        
    def _log(self, message: str):
        """输出日志"""
        print(message)
        if self._log_callback:
            self._log_callback(message)
        
    def test_download(self, test_duration: int = 10) -> Optional[float]:
        """
        测试下载速度
        
        Args:
            test_duration: 测试持续时间（秒）
            
        Returns:
            Optional[float]: 下载速度(Mbps)
        """
        self._log(f"[下载测试] 开始测试下载速度...")
        
        # 使用多个URL测试
        speeds = []
        
        for url, size, name in self.TEST_URLS['download'][:3]:  # 使用前3个URL
            try:
                self._log(f"[下载测试] 正在从 {name} 下载测试...")
                speed = self._test_download_single(url, test_duration)
                if speed > 0:
                    speeds.append(speed)
                    self._log(f"[下载测试] {name}: {speed:.2f} Mbps")
            except Exception as e:
                self._log(f"[下载测试] {name} 测试失败: {e}")
                continue
        
        if speeds:
            # 计算统计信息
            avg_speed = sum(speeds) / len(speeds)
            max_speed = max(speeds)
            min_speed = min(speeds)
            
            self.download_speed = round(avg_speed, 3)
            self.download_stats = {
                'max': round(max_speed, 3),
                'min': round(min_speed, 3),
                'avg': round(avg_speed, 3),
                'speeds': speeds
            }
            
            # 显示详细统计
            self._log(f"[下载测试] ========== 下载速度统计 ==========")
            self._log(f"[下载测试] 最高速度: {max_speed:.2f} Mbps ({max_speed / 8:.2f} MB/s)")
            self._log(f"[下载测试] 最低速度: {min_speed:.2f} Mbps ({min_speed / 8:.2f} MB/s)")
            self._log(f"[下载测试] 平均速度: {avg_speed:.2f} Mbps ({avg_speed / 8:.2f} MB/s)")
            self._log(f"[下载测试] =====================================")
            return self.download_speed
        else:
            self._log(f"[下载测试] 所有测试都失败")
            return None
            
    def _test_download_single(self, url: str, duration: int = 10) -> float:
        """
        单个URL下载测试
        
        Args:
            url: 测试URL
            duration: 测试持续时间
            
        Returns:
            float: 下载速度(Mbps)
        """
        start_time = time.time()
        downloaded = 0
        downloaded_chunks = []  # 保存下载的数据块
        
        try:
            # 添加User-Agent避免被拦截
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, stream=True, timeout=30, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded += len(chunk)
                    downloaded_chunks.append(chunk)  # 保存数据块
                    
                # 检查是否超时
                elapsed = time.time() - start_time
                if elapsed >= duration:
                    break
            
            elapsed = time.time() - start_time
            if elapsed > 0 and downloaded > 0:
                # 保存下载的数据用于上传测试
                self._downloaded_data = b''.join(downloaded_chunks)
                self._log(f"[下载测试] 已保存 {len(self._downloaded_data) / (1024*1024):.2f} MB 数据用于上传测试")
                
                # 计算速度: (字节数 * 8) / 时间 / 1,000,000 = Mbps
                speed_mbps = (downloaded * 8) / elapsed / 1_000_000
                return speed_mbps
            
        except requests.exceptions.Timeout:
            self._log(f"[下载测试] 连接超时")
        except requests.exceptions.ConnectionError:
            self._log(f"[下载测试] 连接失败")
        except requests.exceptions.HTTPError as e:
            self._log(f"[下载测试] HTTP错误: {e.response.status_code}")
        except Exception as e:
            self._log(f"[下载测试] 下载出错: {e}")
            
        return 0.0
        
    def test_upload(self, test_size_mb: int = 100) -> Optional[float]:
        """
        测试上传速度
        
        Args:
            test_size_mb: 测试数据大小(MB)，默认100MB（如果有下载数据则使用下载数据）
            
        Returns:
            Optional[float]: 上传速度(Mbps)
        """
        self._log(f"[上传测试] 开始测试上传速度...")
        
        # 使用下载的数据或生成新数据
        if self._downloaded_data and len(self._downloaded_data) > 0:
            test_data = self._downloaded_data
            self._log(f"[上传测试] 使用下载的 {len(test_data) / (1024*1024):.2f} MB 数据进行上传测试")
        else:
            test_data = b'0' * (test_size_mb * 1024 * 1024)
            self._log(f"[上传测试] 使用生成的 {test_size_mb} MB 数据进行上传测试")
        
        speeds = []
        
        # 多次上传测试以获得更准确的统计
        test_count = 3  # 测试3次
        for i in range(test_count):
            for url, name in self.TEST_URLS['upload'][:1]:  # 只使用第一个URL
                try:
                    self._log(f"[上传测试] 第{i+1}次向 {name} 上传测试...")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    start_time = time.time()
                    response = requests.post(url, data=test_data, timeout=30, headers=headers)
                    elapsed = time.time() - start_time
                    
                    if response.status_code == 200 and elapsed > 0:
                        # 计算速度
                        speed_mbps = (len(test_data) * 8) / elapsed / 1_000_000
                        speeds.append(speed_mbps)
                        self._log(f"[上传测试] {name}: {speed_mbps:.2f} Mbps ({speed_mbps / 8:.2f} MB/s)")
                        
                except Exception as e:
                    self._log(f"[上传测试] {name} 测试失败: {e}")
                    continue
        
        # 上传完成后清理下载的数据
        if self._downloaded_data:
            self._log(f"[上传测试] 清理下载数据...")
            self._downloaded_data = None
        
        if speeds:
            # 计算统计信息
            avg_speed = sum(speeds) / len(speeds)
            max_speed = max(speeds)
            min_speed = min(speeds)
            
            self.upload_speed = round(avg_speed, 3)
            self.upload_stats = {
                'max': round(max_speed, 3),
                'min': round(min_speed, 3),
                'avg': round(avg_speed, 3),
                'speeds': speeds
            }
            
            # 显示详细统计
            self._log(f"[上传测试] ========== 上传速度统计 ==========")
            self._log(f"[上传测试] 最高速度: {max_speed:.2f} Mbps ({max_speed / 8:.2f} MB/s)")
            self._log(f"[上传测试] 最低速度: {min_speed:.2f} Mbps ({min_speed / 8:.2f} MB/s)")
            self._log(f"[上传测试] 平均速度: {avg_speed:.2f} Mbps ({avg_speed / 8:.2f} MB/s)")
            self._log(f"[上传测试] =====================================")
            return self.upload_speed
        else:
            self._log(f"[上传测试] 所有测试都失败")
            return None
            
    def test_ping(self, hosts: list = None) -> Optional[Dict]:
        """
        测试Ping延迟
        
        Args:
            hosts: 要测试的主机列表
            
        Returns:
            Optional[Dict]: Ping结果字典
        """
        if hosts is None:
            # 使用国内常用服务和CDN
            hosts = [
                ('www.baidu.com', '百度'),
                ('www.qq.com', '腾讯'),
                ('www.taobao.com', '淘宝'),
                ('www.163.com', '网易'),
                ('www.jd.com', '京东'),
                ('www.aliyun.com', '阿里云'),
                ('cloud.tencent.com', '腾讯云'),
                ('www.huaweicloud.com', '华为云'),
                ('www.bilibili.com', '哔哩哔哩'),
                ('www.douyin.com', '抖音'),
            ]
        
        self._log(f"[Ping测试] 开始测试 {len(hosts)} 个网站的延迟...")
        
        results = {}
        valid_pings = []
        
        for host, name in hosts:
            ping_time = self._ping_http(host)
            results[name] = ping_time
            
            if ping_time is not None:
                valid_pings.append(ping_time)
                self._log(f"[Ping测试] {name} ({host}): {ping_time:.1f} ms")
            else:
                self._log(f"[Ping测试] {name} ({host}): 超时")
        
        if valid_pings:
            avg_ping = round(sum(valid_pings) / len(valid_pings), 1)
            min_ping = round(min(valid_pings), 1)
            max_ping = round(max(valid_pings), 1)
            
            self._log(f"[Ping测试] 统计结果:")
            self._log(f"  - 平均延迟: {avg_ping} ms")
            self._log(f"  - 最小延迟: {min_ping} ms")
            self._log(f"  - 最大延迟: {max_ping} ms")
            self._log(f"  - 成功率: {len(valid_pings)}/{len(hosts)}")
            
            self.ping_time = avg_ping
            
            return {
                'results': results,
                'average': avg_ping,
                'min': min_ping,
                'max': max_ping,
                'success_count': len(valid_pings),
                'total_count': len(hosts)
            }
        else:
            self._log(f"[Ping测试] 所有主机都无法访问")
            return None
            
    def _ping_http(self, host: str) -> Optional[float]:
        """
        使用HTTP请求测试延迟
        
        Args:
            host: 主机地址
            
        Returns:
            Optional[float]: 延迟时间(ms)
        """
        url = f"http://{host}" if not host.startswith('http') else host
        
        try:
            start_time = time.time()
            response = requests.head(url, timeout=5, allow_redirects=True)
            elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
            
            if response.status_code < 500:  # 只要不是服务器错误就算成功
                return elapsed
                
        except Exception as e:
            pass
            
        return None
        
    def cleanup(self):
        """清理临时数据"""
        if self._downloaded_data:
            self._log(f"[清理] 释放下载数据 ({len(self._downloaded_data) / (1024*1024):.2f} MB)")
            self._downloaded_data = None
            
    def __del__(self):
        """析构函数，确保清理"""
        self.cleanup()
        
    def get_results(self) -> Dict:
        """
        获取测试结果
        
        Returns:
            Dict: 测试结果字典
        """
        return {
            'download': self.download_speed,
            'upload': self.upload_speed,
            'ping': self.ping_time,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
